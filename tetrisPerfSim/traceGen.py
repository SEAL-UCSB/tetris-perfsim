'''
Created on Nov 14, 2018

@author: shuangchenli

This file outputs sparse weight data with indext given a DNN model, 
it either (1) generate randomly given a sparse rate or (2) using the data dump from pyTorch
'''

#@ling: maintain this module
import random

class DataBlock():
  def __init__(self):
    self.blockSize = 0*0
    self.coordRow = 0
    self.coordCol = 0
    self.indexRow = []
    self.indexCol = []

class Layer():
  def __init__(self):
    # settings
    self.value = {'Batch':0, 'H':0, 'W':0, 'Cin':0, 'Cout':0, 'Kw':0, 'Ky':0} # assume stride = 1
    self.type = '' #['conv', 'fc'] no other OP is considerred
    self.sparseRatio = 0.0
    self.dataSource = '' #['synthatic','pytorch']
    self.dataWidth = 0 # BYTE
    self.name = ''
    self.blockSizeH = 0  # how many input channels in a block
    self.blockSizeW = 0  # how many output channels in a block
    self.numBlockH = 0  # number of blocks in vertical direction
    self.numBlockW = 0  # number of blocks in horizontal direction
    self.cinShuffle = []
    self.coutShuffle = []
    
    # data structure feed to reorderEngine
    self.numDataBlock = 0
    self.data = [] # list of DataBlock()

class App():
  def __init__(self):
    self.name = ''
    self.numLayer = 0
    self.layers = [] # list of Layer()

# @ling    
def SparseDataGen(layer):
  if(layer.dataSource == 'synthatic'):
    # numBlock
    layer.numBlockH = layer.value['Cin'] / layer.blockSizeH
    layer.numBlockW = layer.value['Cout'] / layer.blockSizeW

    # numDataBlock
    layer.numDataBlock = int(layer.numBlockH * layer.numBlockW * layer.sparseRatio)

    # cinShuffle & coutShuffle
    layer.cinShuffle = [i for i in range(layer.value['Cin'])]
    layer.coutShuffle = [i for i in range(layer.value['Cout'])]
    random.shuffle(layer.cinShuffle)
    random.shuffle(layer.coutShuffle)

    # select blocks randomly
    block_list = random.sample([i for i in range(layer.numBlockH * layer.numBlockW)], layer.numDataBlock)

    # data
    for i in range(layer.numDataBlock):
      layer.data.append(DataBlock())

      # block size
      layer.data[i].blockSize = layer.blockSizeH * layer.blockSizeW

      # coordRow & coordCol
      layer.data[i].coordRow = block_list[i] // layer.numBlockW
      layer.data[i].coordCol = block_list[i] % layer.numBlockW

      # indexRow & indexCol
      row_begin = layer.blockSizeH * layer.data[i].coordRow
      row_end = layer.blockSizeH * (layer.data[i].coordRow + 1)
      layer.indexRow = layer.cinShuffle[row_begin : row_end]

      col_begin = layer.blockSizeW * layer.data[i].coordCol
      col_end = layer.blockSizeW * (layer.data[i].coordCol + 1)
      layer.indexCol = layer.coutShuffle[col_begin : col_end]
  elif(layer.dataSource == 'pytorch'):
    # [TODO] @ling 
    assert(True)
  else:
    assert(False)
  