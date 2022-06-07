import sys
import unittest
from subprocess import check_output

packageName_Maps = 'com.google.android.apps.maps'
packageName_Soundcloud = 'com.soundcloud.android'

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')
testingFlag = 25

import testbed as client

def convert(string):
    string = string.replace("b", '')
    string = string.replace("\'", '')
    string = string.replace('\\n', '')
    string = string.strip()
    string = int(string)
    return string


class TestADBCommand(unittest.TestCase):
    def setUp(self):
        self.longMessage=False

    def test_launch(self):
        for i in range(4, 6):
            with self.subTest(i = i):
                client.main(23)
                client.global_controller.parse_events(client.global_world, client.global_clock, testingFlag, i)
                client.global_world.destroy()
        
        adb_output1 = check_output(['adb shell pidof com.google.android.apps.maps'], shell=True)
        adb_output1 = convert(str(adb_output1))
        adb_output2 = check_output(['adb shell pidof com.soundcloud.android'], shell=True)
        adb_output2 = convert(str(adb_output2))
        
        
        assert isinstance(adb_output1, int)
        assert isinstance(adb_output2, int)

            

if __name__ == '__main__':
    unittest.main()