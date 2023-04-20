import sys
import subprocess
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory-v2/testcases')

packageName = "com.example.jultrautomaintenance"

cmd = f"adb shell 'pm list packages {packageName}'"

#Check is packageName is in the list of installed packages
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

o, e = proc.communicate()
# print('Output: ' + o.decode('ascii'))
# print('Error: '  + e.decode('ascii'))
# print('code: ' + str(proc.returncode))
output = o.decode('ascii')
#print(output)

class TestAPKinstall(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_installation(self):
        isInstalled = False
        if(packageName in output):
            print("APK installed Successfully")
            isInstalled=True
        else:
            isInstalled=False
        self.assertTrue(isInstalled,msg="FAILURE! App was not installed successfully!")

if __name__ == '__main__':
    unittest.main()
