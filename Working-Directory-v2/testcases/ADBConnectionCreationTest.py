import sys
import subprocess
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory-v2/testcases')

cmd = f"adb devices"

#list the connected adb devices
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

o, e = proc.communicate()
output = o.decode('ascii')
print(output)

#check if there is a device with the following prefix in the ip address
ip_prefix = "10.160."

class TestADBconnection(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_connection(self):
        isConnected = False
        if(ip_prefix in output):
            print("ADB Connection is Established Successfully")
            isConnected=True
        else:
            isConnected=False
        self.assertTrue(isConnected,msg="FAILURE! ADB connection was NOT established!")

if __name__ == '__main__':
    unittest.main()