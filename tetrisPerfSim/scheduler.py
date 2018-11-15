'''
Created on Nov 14, 2018

@author: shuangchenli

Compiler Model:
Given a DNN model, this file partition the big gemm into blocks according to the block sparsity,
and then map them to the PE arrays while minimizing the data communication.
'''

#@ling: maintain this module

class PartialLayer():
  def __init__(self):
    # read data from DRAM
    self.weight = [] # list of traceGen.DataBlock()
    # read the non-shuffled fmap from FmapMEM
    self.fmapFromFmapMem = [] # list of traceGen.DataBlock()
    # two tile may need the same fmap data, in this case, data is bypassed by NOC, not FmapMEM
    self.fmapInNoC = [] # list of traceGen.DataBlock()
    # accumuate data from last partial layer, read the after-shuffled block data from ReorderBuf, not FmapMEM
    self.fmapFromReorderBuf = [] # list of traceGen.DataBlock()
    # write the results to FmapMEM, need to convert/reorder the data
    self.fmapToFmapMem = [] # list of traceGen.DataBlock()
    # partial results need to be accumuated in later partial layer, store it in ReorderBuf without convert/reorder
    self.fmapToReorderBuf = [] # list of traceGen.DataBlock()

#@ling
def Partition(tetrisArch, layer): #input: components.TetrisArch(), traceGen.Layer(); output: [PartialLayer()]
  partition = [] # list of ParialLayer
  # [TODO] partition the weight into PE arrays according to the sparse
  return partition

#@ling
def GenFmapRequests(partialLayer): #input PartialLayer()
  assert(True)
  # [TODO] generate fmap blocks
  # partialLayer.fmapFromSRAM.append(xxx)