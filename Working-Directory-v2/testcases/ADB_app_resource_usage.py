import sys
import subprocess
import unittest

packageName = "com.example.jultrautomaintenance"
listThreshold = "100"
cpuThreshold = 10.0
memThreshold = 10.0

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory-v2/testcases')

cmd = f"adb shell pidof {packageName}"

#find pid of app by packageName
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
o, e = proc.communicate()
pid = o.decode('ascii')

#timeout is necessayr or command will run forever
cmd = f"timeout 2s adb shell top -m {listThreshold} | grep {pid}"

#get resource usage of app by pid
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
o, e = proc.communicate()
resource_usage = o.decode('ascii')

resource_usage = resource_usage.split()
cpuUsage = float(resource_usage[8])
memUsage = float(resource_usage[9])

class TestResourceUsage(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_resource_usage(self):
        isBelowThreshold = False
        if cpuUsage <= cpuThreshold and memUsage <= memThreshold:
            isBelowThreshold = True
            print("App is below the CPU and memory utilization thresholds")
        self.assertTrue(isBelowThreshold,msg="FAILURE! App has NOT met CPU and memory usage requirements!")
if __name__ == '__main__':
    unittest.main()