import sys
import subprocess
import unittest
import time

packageName = "com.example.jultrautomaintenance"

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory-v2/testcases')

cmd = f"adb shell am force-stop {packageName}"
cmd2 = f"adb shell pidof {packageName}"

#force stop app based on packageName
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
time.sleep(2)

#check if pid exists for app with packageName
proc = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
o, e = proc.communicate()
output = o.decode('ascii')

class TestKillApp(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_kill(self):
        isKilled = False
        if output == "":
            isKilled = True
            print("App has been killed successfully")
        self.assertTrue(isKilled,msg="FAILURE! App has NOT been killed and is still running!")
if __name__ == '__main__':
    unittest.main()