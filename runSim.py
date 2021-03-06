'''
Created on Nov 14, 2018

@author: shuangchenli
'''

from tetrisPerfSim import configs, perfModel

#@liu
def main():
  #[TODO] @liu: setup the pool
  hardwarePool = ['dense']
  # hardwarePool = ['dense']
  appPool = ['vgg16_dense']
  for selectHW in hardwarePool:
    hardware = configs.DesignSpaceExploration(selectHW)
    hardware.printConfig()
    hardware.resetStatus()
    for selectAPP in appPool:
      app = configs.Benchmarking(selectAPP, hardware)
      for layer in app.layers:
        perfModel.Sim(hardware, layer)

        if hardware.numLayer == 0:
          hardware.layerStats[0,0] = hardware.totalEnergy
          hardware.layerStats[1,0] = hardware.totalLatency
        else:
          hardware.layerStats[0, hardware.numLayer] = hardware.totalEnergy - hardware.layerStats[0, hardware.numLayer - 1]
          hardware.layerStats[1, hardware.numLayer] = hardware.totalLatency - hardware.layerStats[1, hardware.numLayer - 1]
        hardware.numLayer += 1
        #hardware.reset()
        #hardware.printResult(2)
      hardware.printResult(2)
      
  
if __name__ == '__main__':
    main()
    
    
