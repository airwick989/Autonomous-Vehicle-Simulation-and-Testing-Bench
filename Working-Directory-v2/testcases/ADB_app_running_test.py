import sys
import getopt
import subprocess
import unittest

f=open("fileUploaded.txt","r")
packageName = f.read()
print(packageName)

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory-v2')
import adblib

installed = str(adblib.device.shell('adb shell am start -n '+packageName+'/'+packageName+'.MainActivity'))

class TestAppRunning(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    
    def test_CPU_usage(self):
        if(len(packageName)>=15):
            packageNameCut = packageName[0:15]+"+"
        cpuData= str(adblib.device.shell("adb shell top -n 1 | FINDSTR "+packageNameCut))
        self.assertNotEqual(cpuData,"",msg="FAILURE! Something went wrong! App is not running!")
if __name__ == '__main__':
    unittest.main()