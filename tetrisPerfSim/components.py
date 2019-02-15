'''
Created on Nov 14, 2018

@author: shuangchenli

Hardware Circuit Model:
This file defines the hardware classes of all the components, and the whole architecture
including SRAM (Unified buffer for Fmap), DRAM (for Weight only, first Fmap assume to come from PCIe), PE, and NoC
Note: all latency is 'ns', energy is 'nj', power is 'uW', area is 'um2', data/width is 'BYTE', bandwidh is GB/s (B/ns)
'''

#@jilan: maintain this module

#@jilan
class SRAM():
  # multi-bank SRAM. Could be NVM so we have both read/write configurations
  # the performance is not merely modeled by numData/BW, 
  # instead, precisely model the bank parallelsim/conflict according the access adr
  # circuit PPA can be achieved from NVSIM/CACTI
  
  # Simulation is based on: fully-associative L2 CACHE in CACTI, 45nm technology
  def __init__(self, _numBank = 0, _widthPerBank = 0, _capacityPerBank = 0, _adrHashScheme = 'ideal', _reorderBufLen = 0):
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
    self.area = 483662*_numBank # um2; is calculated by combanition of banks
    # CACTI does not give write energy/time but access energy/time
    self.readLatency = 0.2962*_numBank # ns
    self.writeLatency = 0.2962*_numBank
    self.readEnergy = 0.01967*_numBank
    self.writeEnergy = 0.01967*_numBank
    self.leakage = 14.6739*_numBank #uw
    
    # statics initialization
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
    
    # internal status (for bank parallelsim/conflict modeling)
    self.bankOccupied = [True] * self.numBank
   
  def setup(self, _numBank = 0, _widthPerBank = 0, _capacityPerBank = 0, _adrHashScheme = 'ideal', _reorderBufLen = 0):
    # structure config
    self.numBank = _numBank
    self.widthPerBank = _widthPerBank # BYTE
    self.capacityPerBank = _capacityPerBank #BYTE
    self.width = self.numBank * self.widthPerBank # BYTE
    self.capacity = self.numBank * self.capacityPerBank #BYTE 
    
  def calcPPA(self):
    # [TODO] @jilan
    # circuit PPA according to the configuration and CACTI etc
    assert(True)
  
  def resetStatus(self):
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
    self.bankOccupied = [True] * self.numBank
 
#@jilan     
class DRAM():
  # DRAM performance is only by BW, i.e., perf = numData/BW
  # circuit PPA can be copied from DDR/HMB spec
  def __init__(self, _numChannel = 0, _standard = 0, _capacityPerChannel = 0):
    # structure config
    self.numChannel = _numChannel
    self.standard = _standard #['DDR3-xxxx', 'DDR4-xxxx', 'HBM2', etc]
    self.capacityPerChannel = _capacityPerChannel
    self.capacity = self.numChannel * self.capacityPerChannel #BYTE
    
    # circuit PPA initialization
    self.width = 0 # BYTE
    self.widthPerChannel = 0 # BYTE
    self.BW = 0 # BTYE/s
    self.energyPerBit = 0 # nj/bit
    self.leakage = 0 # uw

    # statics 
    self.numAccess= 0
    self.avgBW = 0
    self.totalReadEnergy = 0
    self.totalWriteEnergy = 0
    self.totalEnergy = 0
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
    assert(True)
    
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
    # 16, 2, 'INT', 256*2, 32*32*2, 256*2
    self.nMAC = _nMAC # need to be 4^n  - n^2?
    self.widthMAC = _widthMAC # BYTE
    self.dataType = _dataType # ['FP', 'INT']
    self.capacityUnifiedBuffer = _capacityUnifiedBuffer # unified buffer according to TPU
    self.capacityAccumulator = _capacityAccumulator # the accumulator buffer in TPU
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
    self.numMAC = 0
    self.numBlock = 0
    self.avgUtilization = 0
    self.totalEnergy = 0
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
    # [TODO] @jilan   
    # circuit PPA according to the configuration and DC etc
    assert(True)
    
  def resetStatus(self):
    self.numMAC = 0
    self.numBlock = 0
    self.avgUtilization = 0
    self.totalEnergy = 0
    self.totalLatency = 0
      
#@jilan
class reorderDMA():
  # input index, output adr to the SRAM to read Fmap from SRAM to PE array
  # input index, output adr and send Fmap from PE to SRAM
  # circuit PPA results from verilog and DC, write HLS or CHISEL
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
  def __init__(self, _numTile = 0, _bandwidthPerTile = 0):
    # structure config
    self.numTile = _numTile
    self.bandwidthPerTile = _bandwidthPerTile
    self.bandwidthTotal = self.numTile * self.bandwidthPerTile
    self.topology = '' # Not used, e.g., 2D mesh
    
    # circuit PPA initialization
    self.areaPerTile = 0
    self.energyPerByte = 0
    self.avgLantecy = 0 # Not used
    
    # statics
    self.dataAmount = 0
    self.totalEnergy = 0
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
    assert(True)
    
  def resetStatus(self):
    self.dataAmount = 0
    self.totalEnergy = 0
    self.totalLatency = 0
        
#@jilan   
class TetrisArch():
  def __init__(self, _type = 'block-sparse', _numTile = 0, _sparseBlockSize = 0, _sparseSource = 'synthatic'):
    # purpose config
    self.type = _type # ['block-sparse', 'dense', 'element-sparse']
    # structure config
    self.numTile = _numTile # should be n^2
    self.sparseBlockSize = _sparseBlockSize # should be n^2
    self.sparseSource = _sparseSource # 'synthatic' or 'pyTorch'
    
    
    # components creation
    self.noc = NoC()
    self.offMem = DRAM()
    self.fmapMem = SRAM()
    self.tile = Tile()
    self.reorder = reorderDMA()
    self.accBuf = SRAM()
    
    #statics
    self.totalLatency = 0
    self.totalEnergy = 0
    
    # asserts [TODO] @jilan
    assert(self.sparseBlockSize == self.singleTile.nMAC), 'sparse block size should be consisant with Tile size'
    assert(self.numTile == self.reorder.numParallelBlocks)
    assert(self.sparseBlockSize == self.reorder.sizeBlock)

  def setup(self, _type = 'block-sparse', _numTile = 0, _sparseBlockSize = 0, _sparseSource = 'synthetic'):
    # purpose config
    self.type = _type # ['block-sparse', 'dense', 'element-sparse']
    # structure config
    self.numTile = _numTile # should be n^2
    self.sparseBlockSize = _sparseBlockSize # should be n^2
    self.sparseSource = _sparseSource # 'synthatic' or 'pyTorch'
      
  def resetStatus(self):
    self.totalLatency = 0
    self.totalEnergy = 0
    # [TODO] @jilan reset statics for every components
   
  def printConfig(self):
    # [TODO] @jilan
    print "========"
  
  def printResult(self, level): # input: int
    # [TODO] @jilan
    print "=========="
    
    
    
