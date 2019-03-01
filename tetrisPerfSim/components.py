'''
Created on Nov 14, 2018

@author: shuangchenli

Hardware Circuit Model:
This file defines the hardware classes of all the components, and the whole architecture
including SRAM (Unified buffer for Fmap), DRAM (for Weight only, first Fmap assume to come from PCIe), PE, and NoC
Note: all latency is 'ns', energy is 'nj', power is 'uW', area is 'um2', data/width is 'BYTE', bandwidh is GB/s (B/ns)
'''

# @jilan: maintain this module - hhh

import numpy as np

# @jilan
class SRAM():
  # multi-bank SRAM. Could be NVM so we have both read/write configurations
  # the performance is not merely modeled by numData/BW, 
  # instead, precisely model the bank parallelsim/conflict according the access adr
  # circuit PPA can be achieved from NVSIM/CACTI
  
  # Simulation is based on: fully-associative L2 CACHE in CACTI, 45nm technology
  def __init__(self, _numBank = 8, _widthPerBank = 1, _capacityPerBank = 64*1024, _adrHashScheme = '', _reorderBufLen = 0):
    # structure config
    self.numBank = _numBank           
    self.widthPerBank = _widthPerBank # BYTE
    self.capacityPerBank = _capacityPerBank #BYTE
    self.width = self.numBank * self.widthPerBank # BYTE
    self.capacity = self.numBank * self.capacityPerBank # BYTE
    
    # other config
    self.adrHashScheme = _adrHashScheme # e.g., ['modN','ideal']
    self.reorderBufLen = _reorderBufLen # 0 length means in-order read
        
    # circuit PPA initialization
    self.readEnergyPerBank = 0
    self.area = 0*_numBank # um2; is calculated by combanition of banks
    # CACTI does not give write energy/time but access energy/time
    self.readLatency = 0*_numBank # ns
    self.writeLatency = 0*_numBank
    self.readEnergy = 0*_numBank
    self.writeEnergy = 0*_numBank
    self.leakage = 0*_numBank #uw
    self.readEnergyPerBank = 0 # uw
    self.readWritePerBank = 0 # uw
    
    # statics initialization
    self.extraEnergy = 0
    self.extraLatency = 0
    self.numRead = 0
    self.numWrite = 0
    self.numBankConflict = 0
    self.avgBW = 0
    self.avgCapacity = 0
    self.totalReadEnergy = 0
    self.totalWriteEnergy = 0
    self.totalEnergy = 0
    self.totalReadLatency = 0
    self.totalWriteLatency = 0
    self.totalLatency = 0
    self.wholeEnergy = 0
    
    # internal status (for bank parallelsim/conflict modeling)
    self.bankOccupied = [True] * self.numBank
   
  def setup(self, _numBank = 0, _widthPerBank = 0, _capacityPerBank = 0, _adrHashScheme = '', _reorderBufLen = 0):
    # structure config
    self.numBank = _numBank
    self.widthPerBank = _widthPerBank # BYTE
    self.capacityPerBank = _capacityPerBank #BYTE
    self.width = self.numBank * self.widthPerBank # BYTE
    self.capacity = self.numBank * self.capacityPerBank #BYTE 

    # other config
    self.adrHashScheme = _adrHashScheme # e.g., ['modN','ideal']
    self.reorderBufLen = _reorderBufLen # 0 length means in-order read
    
  def calcPPA(self):
    # [TODO] @jilan
    # circuit PPA according to the configuration and NVSim
    # print self.widthPerBank == 1 and self.capacityPerBank == 512*1024

    if self.widthPerBank == 1 and self.capacityPerBank == 128*1024:
      self.area = 77231.364*self.numBank # um2
      self.readLatency = 13.168 # ns
      self.writeLatency = 13.168 # ns
      self.readEnergyPerBank = 7.893e-3 # nj
      self.writeEnergyPerBank = 0.616e-3 # nj
      self.readEnergy = 7.893e-3*self.numBank
      self.writeEnergy = 0.616e-3*self.numBank
      self.leakage = 2.774e3*self.numBank #uw
      
    elif self.widthPerBank == 1 and self.capacityPerBank == 256*1024:
      self.area = 152977.557*self.numBank # um2
      self.readLatency = 14.875 # ns
      self.writeLatency = 14.875 # ns
      self.readEnergyPerBank = 15.137e-3 # nj
      self.writeEnergyPerBank = 0.982e-3 # nj
      self.readEnergy = 15.137e-3*self.numBank
      self.writeEnergy = 0.982e-3*self.numBank
      self.leakage = 5.533e3*self.numBank #uw
      
    elif self.widthPerBank == 1 and self.capacityPerBank == 512*1024:
      self.area = 301895.790*self.numBank # um2
      self.readLatency = 33.129 # ns
      self.writeLatency = 33.129 # ns
      self.readEnergyPerBank = 29.628e-3 # nj
      self.writeEnergyPerBank = 1.268e-3 # nj
      self.readEnergy = 29.628e-3*self.numBank
      self.writeEnergy = 1.268e-3*self.numBank
      self.leakage = 11.05e3*self.numBank #uw
            
    elif self.widthPerBank == 1 and self.capacityPerBank == 1024*1024:
      self.area = 604079.646*self.numBank # um2
      self.readLatency = 37.745 # ns
      self.writeLatency = 37.745 # ns
      self.readEnergyPerBank = 58.188e-3 # nj
      self.writeEnergyPerBank = 2.048e-3 # nj
      self.readEnergy = 58.188e-3*self.numBank
      self.writeEnergy = 2.048e-3*self.numBank
      self.leakage = 22.075e3*self.numBank #uw
                  
    elif self.widthPerBank == 1 and self.capacityPerBank == 2048*1024:
      self.area = 1.203e6*self.numBank # um2
      self.readLatency = 46.64 # ns
      self.writeLatency = 46.64 # ns
      self.readEnergyPerBank = 115.393e-3 # nj
      self.writeEnergyPerBank = 3.691e-3 # nj
      self.readEnergy = 115.393e-3*self.numBank
      self.writeEnergy = 3.691e-3*self.numBank
      self.leakage = 44.118e3*self.numBank #uw

    # =======================2 bytes===============================  
    elif self.widthPerBank == 2 and self.capacityPerBank == 128*1024:
      self.area = 76584.688*self.numBank # um2
      self.readLatency = 13.162 # ns
      self.writeLatency = 13.162 # ns
      self.readEnergyPerBank = 7.925e-3 # nj
      self.writeEnergyPerBank = 0.729e-3 # nj
      self.readEnergy = 7.925e-3*self.numBank
      self.writeEnergy = 0.729e-3*self.numBank
      self.leakage = 2.774e3*self.numBank #uw
      
    elif self.widthPerBank == 2 and self.capacityPerBank == 256*1024:
      self.area = 152973.279*self.numBank # um2
      self.readLatency = 14.87 # ns
      self.writeLatency = 14.87 # ns
      self.readEnergyPerBank = 15.307e-3 # nj
      self.writeEnergyPerBank = 1.207e-3 # nj
      self.readEnergy = 15.307e-3*self.numBank
      self.writeEnergy = 1.207e-3*self.numBank
      self.leakage = 5.533e3*self.numBank #uw
      
    elif self.widthPerBank == 2 and self.capacityPerBank == 512*1024:
      self.area = 301891.517*self.numBank # um2
      self.readLatency = 33.217 # ns
      self.writeLatency = 33.217 # ns
      self.readEnergyPerBank = 29.799e-3 # nj
      self.writeEnergyPerBank = 1.494e-3 # nj
      self.readEnergy = 29.799e-3*self.numBank
      self.writeEnergy = 1.494e-3*self.numBank
      self.leakage = 11.05e3*self.numBank #uw
            
    elif self.widthPerBank == 2 and self.capacityPerBank == 1024*1024:
      self.area = 604072.668*self.numBank # um2
      self.readLatency = 37.751 # ns
      self.writeLatency = 37.751 # ns
      self.readEnergyPerBank = 58.529e-3 # nj
      self.writeEnergyPerBank = 2.497e-3 # nj
      self.readEnergy = 58.529e-3*self.numBank
      self.writeEnergy = 2.497e-3*self.numBank
      self.leakage = 22.075e3*self.numBank #uw
                  
    elif self.widthPerBank == 2 and self.capacityPerBank == 2048*1024:
      self.area = 1.203e6*self.numBank # um2
      self.readLatency = 46.638 # ns
      self.writeLatency = 46.638 # ns
      self.readEnergyPerBank = 116.081e-3 # nj
      self.writeEnergyPerBank = 4.597e-3 # nj
      self.readEnergy = 116.081e-3*self.numBank
      self.writeEnergy = 4.597e-3*self.numBank
      self.leakage = 44.118e3*self.numBank #uw

    else:
      print self.widthPerBank, self.capacityPerBank
      assert(False), 'Unexpected SRAM configurations.'

    '''
    [CACTI 6.0 DATA]

    if self.numBank == 8 and self.widthPerBank == 1 and self.capacityPerBank == 64*1024:
      self.area = 483662*self.numBank # um2; is calculated by combanition of banks
      # CACTI does not give write energy/time but access energy/time
      self.readLatency = 0.2962 # ns
      self.writeLatency = 0.2962
      self.readEnergyPerBank = 0.01967 # uw
      self.writeEnergyPerBank = 0.01967 # uw
      self.readEnergy = 0.01967*self.numBank
      self.writeEnergy = 0.01967*self.numBank
      self.leakage = 14.6739e3*self.numBank #uw
      # assert(False), 'the sram is too small'

    elif self.numBank == 8 and self.widthPerBank == 1 and self.capacityPerBank == 128*1024:
      self.area = 1.006998 * 0.861028e6*self.numBank # um2; is calculated by combanition of banks
      # CACTI does not give write energy/time but access energy/time
      self.readLatency = 0.40877 # ns
      self.writeLatency = 0.40877
      self.readEnergyPerBank = 0.00804587 # nj
      self.writeEnergyPerBank = 0.00804587 # nj
      self.readEnergy = 0.00804587*self.numBank
      self.writeEnergy = 0.00804587*self.numBank
      self.leakage = 9.26774e3*self.numBank #uw

    elif self.numBank == 8 and self.widthPerBank == 1 and self.capacityPerBank == 256*1024:
      self.area = 0.789261 * 1.226993e6*self.numBank # um2; is calculated by combanition of banks
      # CACTI does not give write energy/time but access energy/time
      self.readLatency = 0.515046 # ns
      self.writeLatency = 0.515046
      self.readEnergyPerBank = 0.0109495 # uw
      self.writeEnergyPerBank = 0.0109495 # uw
      self.readEnergy = 0.0109495*self.numBank
      self.writeEnergy = 0.0109495*self.numBank
      self.leakage = 20.3891e3*self.numBank #uw

    elif self.numBank == 8 and self.widthPerBank == 1 and self.capacityPerBank == 512*1024:
      self.area = 1.510042 * 1.30987e6*self.numBank # um2; is calculated by combanition of banks
      # CACTI does not give write energy/time but access energy/time
      self.readLatency = 0.6925 # ns
      self.writeLatency = 0.6925
      self.readEnergyPerBank = 0.0153678 # uw
      self.writeEnergyPerBank = 0.0153678 # uw
      self.readEnergy = 0.0153678*self.numBank
      self.writeEnergy = 0.0153678*self.numBank
      self.leakage = 40.778e3*self.numBank #uw

    elif self.numBank == 8 and self.widthPerBank == 1 and self.capacityPerBank == 1024*1024:
      self.area = 1.532442 * 2.294280e6*self.numBank # um2; is calculated by combanition of banks
      # CACTI does not give write energy/time but access energy/time
      self.readLatency = 0.80164 # ns
      self.writeLatency = 0.80164
      self.readEnergyPerBank = 0.0295372 # uw
      self.writeEnergyPerBank = 0.0295372 # uw
      self.readEnergy = 0.0295372*self.numBank
      self.writeEnergy = 0.029537*self.numBank
      self.leakage = 74.0647e3*self.numBank #uw
      
    elif self.numBank == 16 and self.widthPerBank == 1 and self.capacityPerBank == 512*1024:
      self.area = 2.016154 * 1.302492e6*self.numBank # um2; is calculated by combanition of banks
      # CACTI does not give write energy/time but access energy/time
      self.readLatency = 0.66878 # ns
      self.writeLatency = 0.66878
      self.readEnergyPerBank = 0.031489 # uw
      self.writeEnergyPerBank = 0.031489 # uw
      self.readEnergy = 0.031489*self.numBank
      self.writeEnergy = 0.031489*self.numBank
      self.leakage = 18.2001e3*self.numBank #uw
      print ("hello")
      
    elif self.numBank == 16 and self.widthPerBank == 1 and self.capacityPerBank == 1024*1024:
      self.area = 2.018074 * 2.355567e6 # um2; is calculated by combanition of banks
      # CACTI does not give write energy/time but access energy/time
      self.readLatency = 0.878617 # ns
      self.writeLatency = 0.878617
      self.readEnergyPerBank = 0.052628 # uw
      self.writeEnergyPerBank = 0.052628 # uw
      self.readEnergy = 0.052628*self.numBank
      self.writeEnergy = 0.052628*self.numBank
      self.leakage = 40.7189e3*self.numBank #uw
    else:
      assert(False), 'Unexpected SRAM configurations.'
    '''
  
  def resetStatus(self):
    self.numRead = 0
    self.numWrite = 0
    self.numBankConflict = 0
    self.extraEnergy = 0
    self.extraLatency = 0
    self.avgBW = 0
    self.avgCapacity = 0
    self.totalReadEnergy = 0
    self.totalWriteEnergy = 0
    self.totalEnergy = 0
    self.totalReadLatency = 0
    self.totalWriteLatency = 0
    self.totalLatency = 0
    self.bankOccupied = [True] * self.numBank
 
#@jilan     
class DRAM():
  # DRAM performance is only by BW, i.e., perf = numData/BW
  # circuit PPA can be copied from DDR/HMB spec
  def __init__(self, _numChannel = 2, _standard = 0, _capacityPerChannel = 0):
    # structure config
    # the simulation is based on Micron power calculator for DDR4
    # the defualt # of channel is 2, with total capacity of 8Gb
    # the system clock is 800MHz, read bandwidth is 800MT/s
    self.numChannel = _numChannel
    self.standard = _standard #['DDR3-xxxx', 'DDR4-xxxx', 'HBM2', etc]
    self.capacityPerChannel = _capacityPerChannel
    self.capacity = self.numChannel * self.capacityPerChannel #BYTE
    
    # circuit PPA initialization
    self.width = 16 # BYTE
    self.widthPerChannel = 8 # BYTE
    self.BW = 19.2e9 # BTYE/s
    self.energyPerBit = 18.125*0.001 # nj/bit
    self.readpower = 116.5*1000 # uw
    self.leakage = 50.9*1000 # uw

    # statics 
    self.numAccess= 0
    self.avgBW = 0
    self.totalReadEnergy = 0
    self.totalWriteEnergy = 0
    self.totalEnergy = 0
    self.wholeEnergy = 0
    self.totalLatency = 0

  def setup(self, _numChannel = 0, _standard = 0, _capacityPerChannel = 0):
    # structure config
    self.numChannel = _numChannel
    self.standard = _standard #['DDR3-xxxx', 'DDR4-xxxx', 'HBM2', etc]
    self.capacityPerChannel = _capacityPerChannel
    self.capacity = self.numChannel * self.capacityPerChannel #BYTE
    
  def calcPPA(self):
    # [TODO] @jilan 
    # circuit PPA according to the standard and DRAM spec etc
    if self.numChannel == 2 and self.standard == 'DDR4-2666' and  self.capacityPerChannel == 4e9:
      self.width = 16 # BYTE
      self.widthPerChannel = 8 # BYTE
      self.BW = 21.3e9 * self.numChannel # BTYE/s
      self.energyPerBit = 100/6.4*0.001 * self.numChannel # nj/bit
      self.readpower = 100*1000 * self.numChannel # uw
      self.leakage = 56.2*1000 * self.numChannel # uw
      # self.leakage = 0 * self.numChannel # uw

    elif self.numChannel == 1 and self.standard == 'DDR4-2666' and  self.capacityPerChannel == 8e9:
      self.width = 8 # BYTE
      self.widthPerChannel = 8 # BYTE
      self.BW = 21.3e9 # BTYE/s
      self.energyPerBit = 116.6/64*0.001 # nj/bit
      self.readpower = 116.6*1000 # uw
      self.leakage = 53.4*1000 # uw
      # self.leakage = 0 * self.numChannel # uw

    elif self.numChannel == 2 and self.standard == 'DDR4-2400' and  self.capacityPerChannel == 4e9:
      self.width = 16 # BYTE
      self.widthPerChannel = 8 # BYTE
      self.BW = 19.2e9 * self.numChannel # BTYE/s
      self.energyPerBit = 2*15.578125*0.001 # nj/bit
      self.readpower = 99.7*1000*2 # uw
      self.leakage = 2*54.0*1000 # uw
      # self.leakage = 0 * self.numChannel # uw

    elif self.numChannel == 1 and self.standard == 'DDR4-2400' and  self.capacityPerChannel == 8e9:
      self.width = 8 # BYTE
      self.widthPerChannel = 8 # BYTE
      self.BW = 19.2e9 * self.numChannel # BTYE/s
      self.energyPerBit = 18.203125*0.001 # nj/bit
      self.readpower = 116.5*1000 # uw
      self.leakage = 50.9*1000 # uw
      # self.leakage = 0 * self.numChannel # uw
    else:
      assert(False), 'Unexpected DRAM configuration.'
    
  def resetStatus(self):
    self.numAccess= 0
    self.avgBW = 0
    self.totalReadEnergy = 0
    self.totalWriteEnergy = 0
    self.totalEnergy = 0
    self.totalLatency = 0   

#@jilan    
class Tile(): # a.k.a. PE
  # one Tile is a nxn systolic array, with good enough buffers
  # the performance model only consider #MAC, not the buffer size
  # the buffer size only kick in for circuit area/power calc
  # the circuit PPA comes from CHISEL verilog and the NVSIM/CACTI
  def __init__(self, _nMAC = 0, _widthMAC = 0, _dataType = 'INT', _capacityUnifiedBuffer = 0, _capacityAccumulator = 0, _capacityWeightFIFO = 0):
    # structure config
    # the tpu paras: nMAC = 256*256, widthMAC = 8, unified buffer = 28MB, # accumulator = 256 
    self.nMAC = _nMAC # need to be 4^n  - n^2?
    self.widthMAC = _widthMAC # BYTE
    self.dataType = _dataType # ['FP', 'INT']
    self.capacityUnifiedBuffer = _capacityUnifiedBuffer # unified buffer according to TPU
    self.capacityAccumulator = _capacityAccumulator # the accumulator buffer in TPU
    # we ignore the weight FIFO
    self.capacityWeightFIFO = _capacityWeightFIFO
    
    # circuit PPA initialization
    self.area = 0
    self.areaMAC = 0
    self.areaUB = 0
    self.areaACC = 0
    self.areaFIFO = 0
    self.latencyPerMAC = 0
    self.energyPerMAC = 0
    self.latencyFIFO = 0
    self.energyPerBitFIFO = 0
    self.latencyUB = 0
    self.energyPerBitUB = 0
    self.latencyACC = 0
    self.energyPerBitACC = 0
    self.leakage = 0
    
    # statics
    # self.numMAC = _nMAC
    self.numBlock = 1   #
    self.avgUtilization = 0
    self.totalEnergy = 0
    self.wholeEnergy = 0
    self.totalLatency = 0

  def setup(self, _nMAC = 0, _widthMAC = 0, _dataType = 'INT', _capacityUnifiedBuffer = 0, _capacityAccumulator = 0, _capacityWeightFIFO = 0):
    # structure config
    self.nMAC = _nMAC # need to be 4^n
    self.widthMAC = _widthMAC # BYTE
    self.dataType = _dataType # ['FP', 'INT']
    self.capacityUnifiedBuffer = _capacityUnifiedBuffer # unified buffer according to TPU
    self.capacityAccumulator = _capacityAccumulator # the accumulator buffer in TPU
    self.capacityWeightFIFO = _capacityWeightFIFO
    
  def calcPPA(self):
    if self.nMAC == 16 and self.widthMAC == 8 and self.dataType == 'INT':
      # [TODO] @jilan
      self.area = ((22.0/28)**2)*0.01244113e6  # um^2
      print self.area
      self.areaMAC = 10823.2932578604 * (22.0/28)**2
      # self.areaUB = 0
      self.areaACC = 994.958642567901 * (22.0/28)**2
      # self.areaFIFO = 0
      self.latencyPerMAC = 1e9/(700e6) # ns
      self.power = 0.0059932084e6 * (0.8/0.86)**2 # uw 
      self.energyPerMAC = 0
      self.latencyFIFO = 0
      self.energyPerBitFIFO = 0
      self.latencyUB = 0
      self.energyPerBitUB = 0
      self.latencyACC = 0
      self.energyPerBitACC = 0
      self.leakage = 0.0039094233e6  * (0.8/0.86)
    
    elif self.nMAC == 64 and self.widthMAC == 8 and self.dataType == 'INT':
      # [TODO] @jilan
      self.area = 0.0481898566732414e6 * (22.0/28)**2 # um^2
      self.areaMAC = 43293.1730314416 * (22.0/28)**2
      # self.areaUB = 0
      self.areaACC = 1989.92 * (22.0/28)**2
      # self.areaFIFO = 0
      self.latencyPerMAC = 1/(700e6)# ns
      self.power = 0.0234310697e6   * (0.8/0.86)**2 # uw 
      self.energyPerMAC = 0
      self.latencyFIFO = 0
      self.energyPerBitFIFO = 0
      self.latencyUB = 0
      self.energyPerBitUB = 0
      self.latencyACC = 0
      self.energyPerBitACC = 0
      self.leakage = 0.0155812244e6   * (0.8/0.86)
      
    elif self.nMAC == 256 and self.widthMAC == 8 and dataType == 'INT':
      # [TODO] @jilan
      self.area = 0.189610096796027 * 10^6  * (22.0/28)**2# um^2
      self.areaMAC = 173172.692125766 * (22.0/28)**2
      # self.areaUB = 0
      self.areaACC = 3979.83457027161 * (22.0/28)**2
      # self.areaFIFO = 0
      self.latencyPerMAC = 1/(700e6) # ns
      self.power = 0.0926427510e6  * (0.8/0.86)**2 # uw 
      self.energyPerMAC = 0
      self.latencyFIFO = 0
      self.energyPerBitFIFO = 0
      self.latencyUB = 0
      self.energyPerBitUB = 0
      self.latencyACC = 0
      self.energyPerBitACC = 0
      self.leakage = 0.0625239600e6 * (0.8/0.86)
      
    elif self.nMAC == 1024 and self.widthMAC == 8 and self.dataType == 'INT':
      # [TODO] @jilan
      self.area = 0.752141727390228e6 * (22.0/28)**2 # um^2
      self.areaMAC = 692690.768503066 * (22.0/28)**2
      # self.areaUB = 0
      self.areaACC = 7959.66914054321 * (22.0/28)**2
      # self.areaFIFO = 0
      self.latencyPerMAC = 1/(700e6) # ns
      self.power = 0.3685079485e6  * (0.8/0.86)**2  # uw 
      self.energyPerMAC = 0
      self.latencyFIFO = 0
      self.energyPerBitFIFO = 0
      self.latencyUB = 0
      self.energyPerBitUB = 0
      self.latencyACC = 0
      self.energyPerBitACC = 0
      self.leakage = 0.2502539651e6 * (0.8/0.86)
    else:
      print('For PE, # MAC:', self.nMAC, 'width of a MAC:', self.widthMAC,'data type:', self.dataType)
      assert(False), 'No acceptable paras for PE.'
    
    #self.leakage = 0
    # circuit PPA according to the configuration and DC etc
    # assert(True)
    
  def resetStatus(self):
    # self.numMAC = 0
    # self.numBlock = 0
    # self.avgUtilization = 0
    self.totalEnergy = 0
    self.totalLatency = 0
      
#@jilan
class reorderDMA():
  # input index, output adr to the SRAM to read Fmap from SRAM to PE array
  # input index, output adr and send Fmap from PE to SRAM
  # circuit PPA results from verilog and DC, write HLS or CHISEL
  
  # DMA is 0 - jilan
  def __init__(self, _sizeBlock = 0, _numParallel = 0):  
    # structure config
    self.sizeBlock = _sizeBlock
    self.numParallel = _numParallel
    
    # circuit PPA initialization
    self.area = 0
    self.latencyPerAdr = 0 # average ns per address generated
    self.energyPerAdr = 0 # 
    self.leakage = 0
    
    # statics
    self.processBlocks = 0
    self.totalEnergy = 0
    self.totalLatency = 0

  def setup(self, _sizeBlock = 0, _numParallel = 0):  
    # structure config
    self.sizeBlock = _sizeBlock
    self.numParallel = _numParallel

  def calcPPA(self):
    # [TODO] @jilan   
    # circuit PPA according to the configuration and DC etc
    assert(True)
    
  def resetStatus(self):
    self.processBlocks = 0
    self.totalEnergy = 0
    self.totalLatency = 0
  
#@jilan    
class NoC():
  # the interconnection between PEs
  # use a fuzzy NOC to model that, similar with MAESTRO, performance only consider total NOC BW
  # circuit PPA does not considerred at this point
  
  # comments_by_jilan: we only model the bw, the communication within PE are modeled by accumulate buffer
  # bandwidth: GB/s
  def __init__(self, _numTile = 0, _bandwidthPerTile = 0):
    # structure config
    self.numTile = _numTile
    self.bandwidthPerTile = _bandwidthPerTile
    self.bandwidthTotal = self.numTile * self.bandwidthPerTile
    self.topology = '' # Not used, e.g., 2D mesh
    
    # circuit PPA initialization
    self.areaPerTile = 0
    self.energyPerByte = 0
    self.avgLatecy = 0 # Not used
    
    # statics
    self.dataAmount = 0
    self.totalEnergy = 0
    self.wholeEnergy = 0
    self.totalLatency = 0
 
  def setup(self, _numTile = 0, _bandwidthPerTile = 0):
    # structure config
    self.numTile = _numTile
    self.bandwidthPerTile = _bandwidthPerTile
    self.bandwidthTotal = self.numTile * self.bandwidthPerTile
    self.topology = '' # Not used, e.g., 2D mesh

  def calcPPA(self):
    # [TODO] @jilan     
    # circuit PPA according to the configuration and DC etc
    if True:
      self.energyPerByte = 0.002097 #pj
    # assert(True)
    
  def resetStatus(self):
    self.dataAmount = 0
    self.totalEnergy = 0
    self.totalLatency = 0
        
#@jilan   
class TetrisArch():
  def __init__(self, _type = 'block-sparse', _numTile = 0, _sparseBlockSize = 0, _sparseSource = 'synthetic'):
    # purpose config
    self.type = _type # ['block-sparse', 'dense', 'element-sparse']
    # structure config
    self.numTile = _numTile # should be n^2 - maybe not, jilan
    self.sparseBlockSize = _sparseBlockSize # should be n^2 - maybe n
    self.sparseSource = _sparseSource # 'synthetic' or 'pyTorch'
    self.layerStats = np.zeros((2,200))
    self.numLayer = 0
    
    # components creation
    self.noc = NoC()
    self.offMem = DRAM()
    self.fmapMem = SRAM()
    self.tile = Tile()
    # self.reorder = reorderDMA() # not used
    self.accBuf = SRAM()
    
    #statics
    self.totalLatency = 0
    self.totalEnergy = 0
    self.conflictLatency = 0
    
    # asserts [TODO] @jilan
    assert(self.sparseBlockSize == self.tile.nMAC), 'sparse block size should be consisant with Tile size'
    # assert(self.numTile == self.reorder.numParallelBlocks)
    # assert(self.sparseBlockSize == self.reorder.sizeBlock)

  def setup(self, _type = 'block-sparse', _numTile = 0, _sparseBlockSize = 0, _sparseSource = 'synthetic'):
    # purpose config
    self.type = _type # ['block-sparse', 'dense', 'element-sparse']
    # structure config
    self.numTile = _numTile # should be n^2
    self.sparseBlockSize = _sparseBlockSize # should be n^2
    self.sparseSource = _sparseSource # 'synthatic' or 'pyTorch'
      
  def resetStatus(self):
    self.layerStats = np.zeros((2,200))
    self.numLayer = 0
    self.totalLatency = 0
    self.totalEnergy = 0
    self.tile.resetStatus()
    self.accBuf.resetStatus()
    self.offMem.resetStatus()
    self.fmapMem.resetStatus()
    self.noc.resetStatus()
    # [TODO] @jilan reset statics for every components
   
  def printConfig(self):
    # [TODO] @jilan
    print " "
    print "====================Tetris Configurations===================="
    print "Technology: 45nm"
    print "System clock: 700MHz"
    print "PE:"
    print "  - Number of PEs: ", self.numTile
    print "  - Size: %d x %d" % (self.tile.nMAC**0.5, self.tile.nMAC**0.5)
    print "Unified Buffer (SRAM): ", self.fmapMem.capacity/(2**20), "MB"
    print "Accumulate Buffer (SRAM): ", self.accBuf.capacity/(2**20), "MB"
    print "Off-chip Memory (DRAM):", self.offMem.capacity/1e9, "GB"
    print "  - Standard: ",self.offMem.standard
    print "  - Number of Channels: ", self.offMem.numChannel, "channel(s)"
    print "The bandwidth of NoC: ", self.noc.bandwidthTotal/1e9, "GB/s"
    # print "============================================================="
    print " "
  
  def printResult(self, level): # input: int
    # [TODO] @jilan
    print "===========================Results==========================="
    print "Summary:"
    print "The system throughput: ", 1e9/self.totalLatency, "images / s"

    print "The total energy consumption: ", self.totalEnergy/1e3, "uj / image"
    print "  - DRAM              : %.3f%%" % (100 * self.offMem.wholeEnergy/self.totalEnergy)
    print "  - Unified Buffer    : %.3f%%" % (100 * self.fmapMem.wholeEnergy/self.totalEnergy)
    print "  - Accumulate Buffer : %.3f%%:" % (100 * self.accBuf.wholeEnergy/self.totalEnergy)
    print "  - PEs               : %.3f%%" % (100 * self.numTile * self.tile.wholeEnergy/self.totalEnergy)
    print "  - NoC               : %.3f%%" % (100 * self.noc.wholeEnergy/self.totalEnergy)


    totalarea = self.fmapMem.area + self.tile.area * self.numTile + self.accBuf.area
    print "The total area: ", totalarea, "um^2"
    print("    - Unified Buffer    (%.2f%%): %.2fum^2" % (100 * self.fmapMem.area/totalarea, self.fmapMem.area))
    print("    - Accumulate Buffer (%.2f%%): %.2fum^2" % (100 * self.accBuf.area/totalarea, self.accBuf.area))
    print("    - MACs              (%.2f%%): %.2fum^2" % (100 * self.tile.areaMAC * self.numTile/totalarea, self.tile.areaMAC * self.numTile))
    print("    - Accumulators      (%.2f%%): %.2fum^2" % (100 * self.tile.areaACC * self.numTile/totalarea, self.tile.areaACC * self.numTile))
    print("    - PEs               (%.2f%%): %.2fum^2" % (100 * self.tile.area * self.numTile/totalarea, self.tile.area * self.numTile))

    print "Bank Conflict / Total Latency:", self.conflictLatency/self.totalLatency
    print " "
    print "======================Layer Statistics======================"
    for k in range(self.numLayer):
      print ("Layer -%2d:   %.3f uj   %.3f us" % (k, 1e3 * self.layerStats[0,k], 1e3 * self.layerStats[1,k]))