'''
Created on Nov 14, 2018

@author: shuangchenli
'''

from tetrisPerfSim import configs, perfModel

#@liu
def main():
  #[TODO] @liu: setup the pool
  hardwarePool = ['dense']
  appPool = ['vgg16']
  for selectHW in hardwarePool:
    hardware = configs.DesignSpaceExploration(selectHW)
    hardware.printConfig()
    hardware.resetStatus()
    for selectAPP in appPool:
      app = configs.Benchmarking(selectAPP, hardware)
      for layer in app.layers:
        perfModel.Sim(hardware, layer)
        #hardware.reset()
        #hardware.printResult(2)
      hardware.printResult(2)
      
  
if __name__ == '__main__':
    main()
    
    
