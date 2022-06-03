import sys
import getopt
import subprocess
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')
import adblib

f=open("fileUploaded.txt","r")
packageName = f.read()
print(packageName)
installed = adblib.device.shell('pm list packages com.example.musicplayer')
print (installed)
class TestADB(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_installation(self):
        isInstalled = False
        if(packageName in installed):
            print("APK installed Successfully")
            isInstalled=True
        else:
            isInstalled=False
        self.assertTrue(isInstalled,msg="FAILURE! App was not installed successfully!")

if __name__ == '__main__':
    unittest.main()
