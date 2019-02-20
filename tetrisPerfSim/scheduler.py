'''
Created on Nov 14, 2018

@author: shuangchenli

Compiler Model:
Given a DNN model, this file partition the big gemm into blocks according to the block sparsity,
and then map them to the PE arrays while minimizing the data communication.
'''

#@ling: maintain this module
import math
import numpy as np
from tetrisPerfSim import reorderEngine, components

class PartialLayer():
  def __init__(self):
    # read data from DRAM
    self.weight = {'byte':0, 'dataAdr':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()
    
    # read the non-shuffled fmap from FmapMEM
    self.fmapFromFmapMem = {'byte':0, 'dataAdr':[]} # 'byte': data size; 'data': list of traceGen.DataBlock()
    
    # two tile may need the same fmap data, in this case, data is bypassed/duplicated by NOC, not FmapMEM
    # this variable records the extra data duplicated by NoC
    self.dupFmapInNoC = {'byte':0, 'dataAdr':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()

    # calculate addition between two PE through NOC
    self.accFmapInNoc = {'bypte':0, 'dataAdr':[]}
    
    # accumuate data from last partial layer, read the after-shuffled block data from ReorderBuf, not FmapMEM
    self.fmapFromAccBuf = {'byte':0, 'dataAdr':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()
    
    # write the results to FmapMEM, need to convert/reorder the data
    self.fmapToFmapMem = {'byte':0, 'dataAdr':[]} # 'byte': data size; 'data': list of traceGen.DataBlock()
    
    # partial results need to be accumuated in later partial layer, store it in ReorderBuf without convert/reorder
    self.fmapToAccBuf = {'byte':0, 'dataAdr':[]} # 'byte': data size; 'data': not used, list of traceGen.DataBlock()

#@ling
def Partition(tetrisArch, layer): #input: components.TetrisArch(), traceGen.Layer(); output: [PartialLayer()]
  partition = [] # list of ParialLayer
  # [TODO] @ling: partition the weight into PE arrays according to the sparse
  # update the 'byte' part of all variables

  FMI_adr, FMO_adr, W_adr = reorderEngine.AdrGen(layer, components.SRAM())
  blockNameList = layer.blockNameList
  dataWidth = tetrisArch.tile.widthMAC
  numTile = tetrisArch.numTile
  numDataBlock = layer.numDataBlock
  numIter = int(math.ceil((numDataBlock * 1.0) / numTile)) # number of required iterations

  finishedBlocks = [] # blocks which have finished calculation
  BlockCol = [0 for i in range(layer.numBlockW)] # output channels which calculated

  for i in range(numIter):
    partition.append(PartialLayer())

    # get the start idx and end idx of blocks in block list
    startID = i * numTile
    endID = (i + 1) * numTile
    if endID > numDataBlock:
      endID = numDataBlock

    iterBlockRow = [] # the selected blocks` row id
    iterBlockCol = [] # the selected blocks` coloumn id
    iterFMO = [] # output fm in each iteration (toMem & toAcc)

    for j in range(startID, endID):
      finishedBlocks.append(layer.data[j].name)

      # weight information
      partition[i].weight['dataAdr'].append(W_adr[j])
      partition[i].weight['byte'] += W_adr.size * dataWidth

      # input FM from mem
      if layer.data[j].coordRow not in iterBlockRow:
        iterBlockRow.append(layer.data[j].coordRow)
        partition[i].fmapFromFmapMem['dataAdr'].append(FMI_adr[j])
        partition[i].fmapFromFmapMem['byte'] += FMI_adr[j].size * dataWidth
      # input FM from NOC
      else:
        partition[i].dupFmapInNoC['dataAdr'].append(FMI_adr[j])
        partition[i].dupFmapInNoC['byte'] += FMI_adr[j].size * dataWidth

      # output FM in each iteration
      if layer.data[j].coordCol not in iterBlockCol:
        iterBlockCol.append(layer.data[j].coordCol)
        iterFMO.append(FMO_adr[j])
      # partial addition between PE through NOC
      else:
        partition[i].accFmapInNoc['dataAdr'].append(FMO_adr[j])
        partition[i].accFmapInNoc['byte'] += FMO_adr[j].size * dataWidth

    for j in range(len(iterBlockCol)):
      # output FM from accumulator
      if BlockCol[iterBlockCol[j]] == 1:
        partition[i].fmapFromAccBuf['dataAdr'].append(iterFMO[j])
        partition[i].fmapFromAccBuf['byte'] += iterFMO[j].size * dataWidth
      else:
        BlockCol[iterBlockCol[j]] = 1

      finished = True
      for block in blockNameList:
        if block not in finishedBlocks:
          finished = False
          break

      # output FM to Mem
      if finished:
        partition[i].fmapToFmapMem['dataAdr'].append(iterFMO[j])
        partition[i].fmapToFmapMem['byte'] += iterFMO[j].size * dataWidth
      # output FM to AccBuffer
      else:
        partition[i].fmapToAccBuf['dataAdr'].append(iterFMO[j])
        partition[i].fmapToAccBuf['byte'] += iterFMO[j].size * dataWidth


  return partition

#@ling
def GenFmapRequests(partialLayer): #input PartialLayer()
  # [TODO] @ling: generate fmap blocks
  # update the 'data' part of partialLayer.fmapFromSRAM and partialLayer.fmapToSRAM
  assert(True)