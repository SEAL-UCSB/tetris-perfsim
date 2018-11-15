'''
Created on Nov 14, 2018

@author: shuangchenli

Hardware Circuit Model:
This file defines the hardware classes of all the components, and the whole architecture
including SRAM (Unified buffer for Fmap), DRAM (for Weight), PE, and NoC
Note: all latency is 'ns', energy is 'nj', power is 'uW', area is 'um2', data/width is 'BYTE', bandwidh is GB/s (B/ns)
'''

#@jilan: maintain this module

class SRAM():
  # multi-bank SRAM. Could be NVM so we have both read/write configurations
  # the performance is not merely modeled by numData/BW, 
  # instead, precisely model the bank parallelsim/conflict according the access adr
  # circuit PPA can be achieved from NVSIM/CACTI
  def __init__(self):
    # structure config
    self.numBank = 0
    self.width = 0 # BYTE
    self.widthPerBank = 0 # BYTE
    self.capacity = 0 #BYTE
    self.capacityPerBank = 0
    
    # other config
    self.adrHashScheme = '' # e.g., ['modN','ideal']
        
    # circuit PPA
    self.area = 0 # um2
    self.readLatency = 0 # ns
    self.writeLatency = 0
    self.readEnergy = 0
    self.writeEnergy = 0
    self.leakage = 0 #uw
    
    # statics 
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
    
    # internal status (for bank parallelsim/conflict modeling
    self.bankOccupied = [True] * self.numBank
    
class DRAM():
  # DRAM performance is only by BW, i.e., perf = numData/BW
  # circuit PPA can be copied from DDR/HMB spec
  def __init__(self):
    # structure config
    self.numChannel = 0
    self.width = 0 # BYTE
    self.widthPerChannel = 64 # BYTE
    self.capacity = 0 #BYTE
    self.capacityPerChannel = 0
    
    # circuit PPA
    self.accessBW = 0
    self.accessEnergy = 0
    self.leakage = 0 #uw
    self.standard = '' # e.g., 'DDR4'

    # statics 
    self.numAccess= 0
    self.avgBW = 0
    self.totalReadEnergy = 0
    self.totalWriteEnergy = 0
    self.totalEnergy = 0
    self.totalLatency = 0
    
class Tile():
  # one Tile is a nxn systolic array, with good enough buffers
  # the performance model only consider #MAC, not the buffer size
  # the buffer size only kick in for circuit area/power calc
  # the circuit PPA comes from CHISEL verilog and the NVSIM/CACTI
  def __init__(self):
    # structure config
    self.nMAC = 0*0 # need to be 4^n
    self.widthMAC = 0 # BYTE
    self.dataType = '' # ['FP', 'INT']
    self.capacityUnifiedBuffer = 0 # unified buffer according to TPU
    self.capacityAccumulator = 0 # the accumulator buffer in TPU
    self.capacityWeightFIFO = 0
    
    # circuit PPA
    self.area = 0
    self.areaMAC = 0
    self.areaUB = 0
    self.areaACC = 0
    self.areaFIFO = 0
    self.latencyPerMAC = 0
    self.energyPerMAC = 0
    self.leakage = 0
    
    # statics
    self.numMAC = 0
    self.numBlock = 0
    self.avgUtilization = 0
    self.totalEnergy = 0
    self.totalLatency = 0

class reorderDMA():
  # input index, output adr to the SRAM to read Fmap from SRAM to PE array
  # input index, output adr and send Fmap from PE to SRAM
  # circuit PPA results from verilog and DC, write HLS or CHISEL
  def __init__(self):  
    # structure config
    self.numParallelBlocks = 0
    self.sizeBlock = 0
    
    # circuit PPA
    self.area = 0
    self.latency = 0
    self.energy = 0
    self.leakage = 0
    
    # statics
    self.processBlocks = 0
    self.totalEnergy = 0
    self.totalLatency = 0
    
class NoC():
  # the interconnection between PEs
  # use a fuzzy NOC to model that, similar with MAESTRO, performance only consider total NOC BW
  # circuit PPA does not considerred at this point
  def __init__(self):
    # structure config
    self.bandwidthPerPort = 0
    self.bandwidthPerTile = 0
    self.bandwidthTotal = 0
    self.topology = '' # e.g., 2D mesh
    
    # circuit PPA
    self.areaPerTile = 0
    self.energyPerByte = 0
    self.avgLantecy = 0
    
    # statics
    self.dataAmount = 0
    self.totalEnergy = 0
    self.totalLatency = 0
    
class TetrisArch():
  def __init__(self):
    # purpose config
    self.type = '' # ['block-sparse', 'dense', 'element-sparse']
    # structure config
    self.numTile = 0*0
    self.sparseBlockSize = 0*0
    
    # components
    self.noc = NoC()
    self.weightMem = DRAM()
    self.fmapMem = SRAM()
    self.tile = Tile()
    self.reorder = reorderDMA()
    self.reorderBuf = SRAM()
    
    #statics
    self.totalLatency = 0
    self.totalEnergy = 0
    
    # asserts
    assert(self.sparseBlockSize == self.singleTile.nMAC), 'sparse block size should be consisant with Tile size'
    assert(self.numTile == self.reorder.numParallelBlocks)
    assert(self.sparseBlockSize == self.reorder.sizeBlock)
  
  #@jilan
  def reset(self):
    self.totalEnergy = 0
    # [TODO] reset statics for every components
   
  #@jilan 
  def printConfig(self):
    # [TODO]
    print "========"
  
  #@jilan
  def printResult(self, level): # input: int
    # [TODO] 
    print "=========="
    
    
    