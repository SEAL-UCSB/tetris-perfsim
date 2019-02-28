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
  tetris = components.TetrisArch()
  # [TODO]: @liu
  if select == 'block-sparse':
    tetris.setup()  #[TODO] @liu setup specific parameters
    tetris.noc.setup()   #[TODO] @liu setup specific parameters
    tetris.offMem.setup()   #[TODO] @liu setup specific parameters
    tetris.fmapMem.setup()   #[TODO] @liu setup specific parameters
    tetris.tile.setup()   #[TODO] @liu setup specific parameters
    #tetris.reorder.setup()   #[TODO] @liu setup specific parameters
    tetris.accBuf.setup()   #[TODO] @liu setup specific parameters
    tetris.noc.calcPPA()
    tetris.noc.resetStatus()
    tetris.offMem.calcPPA()  
    tetris.offMem.resetStatus() 
    tetris.fmapMem.calcPPA()  
    tetris.fmapMem.resetStatus() 
    tetris.tile.calcPPA()   
    tetris.tile.resetStatus()
    #tetris.reorder.calcPPA()   
    #tetris.reorder.resetStatus()
    tetris.accBuf.calcPPA()   
    tetris.accBuf.resetStatus()
    tetris.resetStatus()
  elif select == 'dense':
    tetris.setup('block-sparse', 64, 64, 'synthetic')
    tetris.noc.setup(64, 2e9)   # 2 byte/cycle
    tetris.offMem.setup(2,'DDR4-2666', 4e9)   # @Shuangchen Do we model DRAM?
    tetris.fmapMem.setup(16, 1, 512*1024)
    tetris.tile.setup(16, 8, 'INT', 256*2, 32*32*2, 256*2)   # BYTE
    #tetris.reorder.setup(64, 8)
    tetris.accBuf.setup(8, 1, 256*1024)
    tetris.noc.calcPPA()
    tetris.noc.resetStatus()
    tetris.offMem.calcPPA()  
    tetris.offMem.resetStatus() 
    tetris.fmapMem.calcPPA()  
    tetris.fmapMem.resetStatus() 
    tetris.tile.calcPPA()   
    tetris.tile.resetStatus()
    #tetris.reorder.calcPPA()   
    #tetris.reorder.resetStatus()
    tetris.accBuf.calcPPA()   
    tetris.accBuf.resetStatus()
    tetris.resetStatus()
  elif select == 'element-sparse':
    tetris.setup()  #[TODO] @liu setup specific parameters
    tetris.noc.setup()   #[TODO] @liu setup specific parameters
    tetris.offMem.setup()   #[TODO] @liu setup specific parameters
    tetris.fmapMem.setup()   #[TODO] @liu setup specific parameters
    tetris.tile.setup()   #[TODO] @liu setup specific parameters
    tetris.reorder.setup()   #[TODO] @liu setup specific parameters
    tetris.accBuf.setup()   #[TODO] @liu setup specific parameters
    tetris.noc.calcPPA()
    tetris.noc.resetStatus()
    tetris.offMem.calcPPA()  
    tetris.offMem.resetStatus() 
    tetris.fmapMem.calcPPA()  
    tetris.fmapMem.resetStatus() 
    tetris.tile.calcPPA()   
    tetris.tile.resetStatus()
    tetris.reorder.calcPPA()   
    tetris.reorder.resetStatus()
    tetris.accBuf.calcPPA()   
    tetris.accBuf.resetStatus()
    tetris.resetStatus()
  elif select == 'EIE':
    tetris.setup()  #[TODO] @liu setup specific parameters
    tetris.noc.setup()   #[TODO] @liu setup specific parameters
    tetris.offMem.setup()   #[TODO] @liu setup specific parameters
    tetris.fmapMem.setup()   #[TODO] @liu setup specific parameters
    tetris.tile.setup()   #[TODO] @liu setup specific parameters
    tetris.reorder.setup()   #[TODO] @liu setup specific parameters
    tetris.accBuf.setup()   #[TODO] @liu setup specific parameters
    tetris.noc.calcPPA()
    tetris.noc.resetStatus()
    tetris.offMem.calcPPA()  
    tetris.offMem.resetStatus() 
    tetris.fmapMem.calcPPA()  
    tetris.fmapMem.resetStatus() 
    tetris.tile.calcPPA()   
    tetris.tile.resetStatus()
    tetris.reorder.calcPPA()   
    tetris.reorder.resetStatus()
    tetris.accBuf.calcPPA()   
    tetris.accBuf.resetStatus()
    tetris.resetStatus()
  else:
    assert(False)
  return tetris 

    
# @liu: design the experiment: list the app
# @ling: fill in the app information etc
def Benchmarking(select, hardware): # input: int/string, component.TetrisArch(), output: traceGen.App()
  # add code to fill in different app with different setups (sparse ratio, sourse etc) according to 'select'
  app = traceGen.App()# create app instance
  # [TODO]: @liu
  model_info = {}
  if select == 'vgg16':
    with open('configs/vgg16.json', 'r') as f:
      model_info = json.load(f)['vgg16']
    app.name = select
    app.numLayer = 16
  elif select == 'vgg8':
    with open('configs/vgg8.json', 'r') as f:
      model_info = json.load(f)['vgg8']
    app.name = select
    app.numLayer = 8
  elif select == 'resnet152':
    assert(False)
  else:
    assert(False)

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
    if (i < 13 and select[0:5] == 'vgg16') or (i < 6 and select[0:4] == 'vgg8'):
      app.layers[i].type = 'conv'
    elif (i < 13 and select[0:5] == 'vgg16') or (i < 6 and select[0:4] == 'vgg8'):
      app.layers[i].type = 'fc'
    else:
      assert(False)

    # sparseRatio
    app.layers[i].sparseRatio = 1 - model_info['pruning_rates'][i]

    # dataSource
    app.layers[i].dataSource = hardware.sparseSource #'synthatic'

    # dataWidth
    app.layers[i].dataWidth = 4

    # name
    if (i < 13 and select[0:5] == 'vgg16') or (i < 6 and select[0:4] == 'vgg8'):
      app.layers[i].name = 'conv' + str(i + 1)
    elif i >= 13 and select[0:5] == 'vgg16':
      app.layers[i].name = 'fc' + str(i - 12)
    elif i >= 6 and select[0:4] == 'vgg8':
      app.layers[i].name = 'fc' + str(i - 5)
    else:
      assert(False)
      
    # blockSizeH & blockSizeW
    app.layers[i].blockSizeH = model_info['block_sizes'][i][0]
    app.layers[i].blockSizeW = model_info['block_sizes'][i][1]

    traceGen.SparseDataGen(app.layers[i])


  return app 

