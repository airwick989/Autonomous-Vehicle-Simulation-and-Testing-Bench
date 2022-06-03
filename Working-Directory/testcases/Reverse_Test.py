import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')

import testbed as client
class TestSteeringWheelKit(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_acceleration_input(self):
        client.main(3)
        self.assertLess(client.get_speed(client.global_world),0,"FAILURE! Reverse not working as intended!")
if __name__ == '__main__':
    unittest.main()


