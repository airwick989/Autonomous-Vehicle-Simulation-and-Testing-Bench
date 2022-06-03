import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')

import testbed as client
class TestGearShifterKit(unittest.TestCase):
    def test_brake_input(self):
        client.main(4)
        self.assertLess(client.get_speed(client.global_world),1, "FAILURE! Gear shifter is in park! Car speed should be less than 0!")
if __name__ == '__main__':
    unittest.main()


