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
    self.weight = {'byte':0, 'data':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()
    
    # read the non-shuffled fmap from FmapMEM
    self.fmapFromFmapMem = {'byte':0, 'data':[]} # 'byte': data size; 'data': list of traceGen.DataBlock()
    
    # two tile may need the same fmap data, in this case, data is bypassed/duplicated by NOC, not FmapMEM
    # this variable records the extra data duplicated by NoC
    self.dupFmapInNoC = {'byte':0, 'data':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()
    
    # accumuate data from last partial layer, read the after-shuffled block data from ReorderBuf, not FmapMEM
    self.fmapFromAccBuf = {'byte':0, 'data':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()
    
    # write the results to FmapMEM, need to convert/reorder the data
    self.fmapToFmapMem = {'byte':0, 'data':[]} # 'byte': data size; 'data': list of traceGen.DataBlock()
    
    # partial results need to be accumuated in later partial layer, store it in ReorderBuf without convert/reorder
    self.fmapToAccBuf = {'byte':0, 'data':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()

#@ling
def Partition(tetrisArch, layer): #input: components.TetrisArch(), traceGen.Layer(); output: [PartialLayer()]
  partition = [] # list of ParialLayer
  # [TODO] @ling: partition the weight into PE arrays according to the sparse
  # update the 'byte' part of all variables
  return partition

#@ling
def GenFmapRequests(partialLayer): #input PartialLayer()
  # [TODO] @ling: generate fmap blocks
  # update the 'data' part of partialLayer.fmapFromSRAM and partialLayer.fmapToSRAM
  assert(True)