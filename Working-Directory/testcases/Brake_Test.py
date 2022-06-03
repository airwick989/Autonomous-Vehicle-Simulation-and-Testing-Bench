import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')

import testbed as client
class TestSteeringWheelKit(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_brake_input(self):
        client.main(2)
        self.assertLess(client.get_speed(client.global_world),1,"FAILURE! Brakes are not working as intended!")
if __name__ == '__main__':
    unittest.main()


