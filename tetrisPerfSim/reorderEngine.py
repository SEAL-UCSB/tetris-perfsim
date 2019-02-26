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
# FMI_adr list[np1d for each block]
# FMO_adr list[np1d for each block]
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
  P = 1 * 2  # padding

  if layer.type == 'conv':
    FMI_order_org = np.reshape(np.arange(FMI_C * (FM_H + P) * (FM_W + P)), (FMI_C, (FM_H + P), (FM_W + P))) % numBank
    FMI_order = np.zeros((FMI_C, FM_H * FM_W * Kw * Kh)).astype(int)
    step = Kw * Kh
    for i in range(FM_H):
      for j in range(FM_W):
        begin_idx = (i * FM_W + j) * step
        FMI_order[:, begin_idx: (begin_idx + step)] = np.reshape(FMI_order_org[:, i: i + Kh, j: j + Kw], (FMI_C, step))

    FMO_order = np.reshape(np.arange(FMO_C * FM_H * FM_W), (FMO_C, FM_H * FM_W)) % numBank
    W_order = np.reshape(np.arange(FMI_C * FMO_C * Kw * Kh), (FMI_C, FMO_C, Kw, Kh)) % numBank

  else:
    FMI_order = np.arange(FMI_C) % numBank
    FMO_order = np.arange(FMO_C) % numBank
    W_order = np.reshape(np.arange(FMI_C * FMO_C), (FMI_C, FMO_C)) % numBank

  FMI_adr = [] # adr for each block`s input FM
  FMO_adr = [] # adr for each block`s output FM
  W_adr = [] # adr for each block`s weight

  for block in blockList:
    FMI_adr.append(np.reshape(FMI_order[block.indexRow], -1))
    FMO_adr.append(np.reshape(FMO_order[block.indexCol], -1))
    if layer.type == 'conv':
      W_adr.append(W_order[block.indexRow, block.indexCol, :, :])
    else:
      W_adr.append(W_order[block.indexRow, block.indexCol])

  return FMI_adr, FMO_adr, W_adr
