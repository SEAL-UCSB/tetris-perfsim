'''
Created on Nov 14, 2018

@author: shuangchenli

This file sweeps configuration setups to perform design space exploration
'''
import json
from tetrisPerfSim import components, traceGen

# @liu: design the experiment: list the hardware setup
# @jilan: get the circuit PPA according to the setup
def DesignSpaceExploration(select): # input: int/string; output: components.TetrisArch()
  # add code to fill in different configurations according to 'select'
  # note that the baseline exp setup is also done here
  # baseline-1: all dense: given same configuration, but set sparse rate as 0
  # baseline-2: element sparse on EIE, set tile size as 1 but many tiles, by pass 
  # baseline-3: element sparse on blocked hardware, treate 1x1 as n-by-n
  tetriConfig = components.TetrisArch()
  # [TODO]:
  numPE = 64
  numMUL = 8 
  # set peak throughput to be 512 Gops/sec, PE at 1 GHz frequency.
  localBufSize = 32 # KB
  globalBufSize = 16 # MB
  globalBW = 1024 # byte/cycle. Need to validate againt CACTI
  return tetriConfig 

# @liu: design the experiment: list the app
# @ling: fill in the app information etc
def Benchmarking(select): # input: int/string, output: traceGen.App()
  # add code to fill in different app with different setups (sparse ratio, sourse etc) according to 'select'
  app = traceGen.App()
  # [TODO]:
  model_info = {}
  if select == 'vgg16':
    with open('vgg.json', 'r') as f:
      model_info = json.load(f)['vgg16']
    app.name = select
    app.numLayer = 16

  for i in range(0, app.numLayer):
    # [TODO]:
    app.layers.append(traceGen.Layer())

    #value
    app.layers[i].value = {
      'Batch': model_info['batch'],
      'H': model_info['size_FM'][i][0], 'W': model_info['size_FM'][i][1],
      'Cin': model_info['channel'][i][0], 'Cout': model_info['channel'][i][1],
      'Kh': model_info['size_K'][i][0], 'Kw': model_info['size_K'][i][1]
    }

    # type
    if i < 13:
      app.layers[i].type = 'conv'
    else:
      app.layers[i].type = 'fc'

    # sparseRatio
    app.layers[i].sparseRatio = model_info['pruning_rates'][i]

    # dataSource
    app.layers[i].dataSource = 'synthatic'

    # dataWidth
    app.layers[i].dataWidth = 4

    # name
    if i < 13:
      app.layers[i].name = 'conv' + str(i + 1)
    else:
      app.layers[i].name = 'fc' + str(i - 12)

    # blockSizeH & blockSizeW
    app.layers[i].blockSizeH = model_info['block_sizes'][i][0]
    app.layers[i].blockSizeW = model_info['block_sizes'][i][1]

    traceGen.SparseDataGen(app.layers[i])

  return app 
