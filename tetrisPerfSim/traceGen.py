'''
Created on Nov 14, 2018

@author: shuangchenli

This file outputs sparse weight data with indext given a DNN model, 
it either (1) generate randomly given a sparse rate or (2) using the data dump from pyTorch
'''

#@ling: maintain this module

from cmath import sqrt

class DataBlock():
  def __init__(self):
    self.blockSize = 0*0
    self.coordRow = 0
    self.coordCol = 0
    self.indexRow = [0] * int(sqrt(self.blockSize))
    self.indexCol = [0] * int(sqrt(self.blockSize))

class Layer():
  def __init__(self):
    # settings
    self.value = {'Batch':0, 'H':0, 'W':0, 'Cin':0, 'Cout':0, 'Kw':0, 'Ky':0} # assume stride = 1
    self.type = '' #['conv', 'fc'] no other OP is considerred
    self.sparseRatio = 0.0
    self.dataSource = '' #['synthatic','pytorch']
    self.dataWidth = 0 # BYTE
    self.name = ''
    
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
    # [TODO]
    assert(True)
  elif(layer.dataSource == 'pytorch'):
    # [TODO]
    assert(True)
  else:
    assert(False)
  