'''
Created on Nov 14, 2018

@author: shuangchenli

This file sweeps configuration setups to perform design space exploration
'''

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
  return tetriConfig 

# @liu: design the experiment: list the app
# @ling: fill in the app information etc
def Benchmarking(select): # input: int/string, output: traceGen.App()
  # add code to fill in different app with different setups (sparse ratio, sourse etc) according to 'select'
  app = traceGen.App()
  # [TODO]:
  for i in range(0, app.numLayer):
    # [TODO]:
    traceGen.SparseDataGen(app.layers[i])
  return app 