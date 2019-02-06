'''
Created on Nov 14, 2018

@author: shuangchenli

Simulator:

Performance Model:
The roofline based simulator, takes the sparse data trace input, leverages the shceduler and the reorderEngine,
calculates the intra-core roofline model, inter-core (NoC) roofline model, and the core-mem (SRAM/DRAM w/ reorder) roofline model
also prints status
also have baseline sims

Performance Model for SRAM:
Reading the SRAM with block weight index (multi-bank with effective bank conflicts),
Write the SRAM with the index
'''

#@liu: maintain this module
from tetrisPerfSim import scheduler, reorderEngine

#@jilan
def PerfDRAM(memory, dataAmount): # inputs: components.DRAM(), int
  # [TODO] calc reading DRAM, update statics in memory
  assert(True)

#@ling
def PerfSRAM(memory, address, isREAD): # inputs: components.SRAM(), int, boolean
  # [TODO] calc reading SRAM, update statics in memory
  if(memory.adrHashScheme == 'ideal'):
    # assume maximal bank parallelism zero bank conflict, i.e., no reordering overhead
    assert(True)
  elif(memory.adrHashScheme == 'modN'):
    # NOTE THAT we could have a OOO-read/write queue here
    # NOTE THAT SRAM model need to consider multi-bank parallelsim and conflict stuff
    assert(True)
  else:
    assert(False)
  assert(True)

#@jilan  
def PerfBUF(memory, dataAmount, isREAD): # inputs: components.SRAM(), int, boolean
  # [TODO] calc reading SRAM, update statics in memory
  # NOTE THAT this buffer is modeled simply by BW, assuming maximal bank parallelism and zero bank conflict
  assert(True)

#@jilan  
def PerfNOC(noc, dataAmount): # inputs: components.NoC(), int
  # [TODO] calc reading NoC, update statics in noc
  assert(True)

#@jilan  
def PerfPE(tile, numtask): # inputs: components.Tile(), int
  # [TODO] calc PE computing, update statics in tile
  assert(True)

#@jilan  
def PerfReorder(reorder, totalDataSize): # inputs: components.ReorderDMA(), int
  # [TODO] calc reorder, update statics in reorder
  assert(True)
  
def RoofLine(tetrisArch): # inputs: components.TetrisArch()
  # [TODO] min{ total-PE, total-NOC, total-FmapMem, total-ReorderBuf, total-DRAM }, energy add them all
  # update the TetrisArch statics
  # NOTE: should be accumulative
  assert(True)

#@jilan
def Sim(tetrisArch, layer): # inputs: components.TetrisArch(), traceGen.Layer()
  partition = scheduler.Partition(tetrisArch, layer)
  for partialLayer in partition:
    scheduler.GenFmapRequests(partialLayer)
    
    # calc reading DRAM for weight, update statics in tetrisArch
    totalDataSize = 0 # [TODO] from partialLayer.weight
    PerfDRAM(tetrisArch.weightMem, totalDataSize)
    
    # calc reading Fmap from FmapMem, update statics in tetrisArch
    adr_readFmapMem = reorderEngine.AdrGen(partialLayer.fmapFromFmapMem)
    PerfSRAM(tetrisArch.fmapMem, adr_readFmapMem, True)
    
    # calc reading Fmap from reorderBuffer for accumulation, update statics in tetrisArch
    totalDataSize = 0 # [TODO] from partialLayer.fmapFromReorderBuf
    PerfBUF(tetrisArch.reorderBuf, totalDataSize, True)
    
    # calc reading Fmap from NOC (Fmap reused by two tiles), update statics in tetrisArch
    totalDataSize = 0 # [TODO] from partialLayer.fmapFromReorderBuf
    PerfNOC(tetrisArch.noc, totalDataSize)
    
    # calc reading Fmap from PE (Fmap reused by two tiles), update statics in tetrisArch
    totalTasks = 0 # [TODO] from partialLayer
    PerfPE(tetrisArch.tile, totalTasks) 
    
    # calc writing Fmap to FmapMem, update statics in tetrisArch
    adr_writeFmapMem = reorderEngine.AdrGen(partialLayer.fmapToFmapMem)
    PerfSRAM(tetrisArch.fmapMem, adr_writeFmapMem, False)

    # calc writting Fmap from reorderBuffer for accumulation, update statics in tetrisArch
    totalDataSize = 0 # [TODO] from partialLayer.fmapToReorderBuf
    PerfBUF(tetrisArch.reorderBuf, totalDataSize, False)
    
    # update the reorder engine
    totalDataSize = 0 # [TODO] from partialLayer.fmapFromFmapMem and partialLayer.fmapToFmapMem
    PerfReorder(tetrisArch.reorder, totalDataSize)
    
    # roofline model, min{ total-PE, total-NOC, total-FmapMem, total-ReorderBuf, total-DRAM }
    RoofLine(tetrisArch)
      
  assert(True)