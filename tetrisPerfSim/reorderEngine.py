'''
Created on Nov 14, 2018

@author: shuangchenli

Functional Model:
generate the in-or-out fmap address according to the after-shuffle blocked weight's index
'''

#@ling: maintain this module
#@ling

import numpy as np

# input:
# tranceGen.Layer()
# Sechduler.SRAM()
# output:
# FMI_adr list[np3d]
# FMO_adr list[np3d]
def AdrGen(layer, sram):

  # assume the size of input feature map equals output feature map (stride = 1)
  FM_H = layer.value['H']
  FM_W = layer.value['W']
  FMI_C = layer.value['Cin']
  FMO_C = layer.value['Cout']
  Kw = layer.value['Kw']
  Kh = layer.value['Kh']
  numBank = sram.numBank
  blockList = layer.data

  if layer.type == 'conv':
    FMI_order = np.reshape(np.arange(FMI_C * FM_H * FM_W), (FMI_C, FM_H, FM_W)) % numBank
    FMO_order = np.reshape(np.arange(FMO_C * FM_H * FM_W), (FMO_C, FM_H, FM_W)) % numBank
    W_order = np.reshape(np.arange(FMI_C * FMO_C * Kw * Kh), (FMI_C, FMO_C, Kw, Kh)) % numBank
  else:
    FMI_order = np.arange(FMI_C) % numBank
    FMO_order = np.arange(FMO_C) % numBank
    W_order = np.reshape(np.arange(FMI_C * FMO_C), (FMI_C, FMO_C)) % numBank


  FMI_adr = [] # adr for each block`s input FM
  FMO_adr = [] # adr for each block`s output FM
  W_adr = [] # adr for each block`s weight

  for block in blockList:
    FMI_adr.append(FMI_order[block.indexRow])
    FMO_adr.append(FMO_order[block.indexCol])
    W_adr.append(W_order[block.indexRow, block.indexCol, :, :])

  return FMI_adr, FMO_adr, W_adr