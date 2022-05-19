import sys
import getopt
import subprocess
import unittest
import time
f=open("C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client\\CICD-Framework-Test-Cases\\fileUploaded.txt","r")
packageName = f.read()
print(packageName)
if(len(packageName)>=15):
    packageNameCut = packageName[0:15]+"+"
print(packageNameCut)
cpuData= str(subprocess.check_output("adb shell top -n 1 | FINDSTR "+packageNameCut, shell=True))
cpuData = cpuData.encode().decode()
print(cpuData)
cpuDataArray = cpuData.split()
i =0
for string in cpuDataArray:
    print(string + ' '+str(i))
    i+=1
cpuUsage = float(cpuDataArray[8])
memUsage = float(cpuDataArray[9])
class TestResourceUsage(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_CPU_usage(self):
        time.sleep(1)
        self.assertLessEqual((cpuUsage/400)*100,35, msg="FAILURE! CPU Usage greater than 35%!")
    def test_MEM_usage(self):
        self.assertLessEqual(memUsage,25, msg="FAILURE! Memory Usage greater than 25%!")
if __name__ == '__main__':
    unittest.main()