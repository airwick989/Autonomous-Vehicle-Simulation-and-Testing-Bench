import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')
testingFlag = 23

import testbed as client
class TestHandBrake(unittest.TestCase):
    def setUp(self):
        self.longMessage=False

    def test_shifter(self):
        for i in range(0, 8):
            with self.subTest(i = i):
                client.main(23)
                if i != 7:
                    self.assertEqual(client.global_controller.parse_events(client.global_world, client.global_clock, testingFlag, i), i+1)
                else:
                    self.assertEqual(client.global_controller.parse_events(client.global_world, client.global_clock, testingFlag, i), -1)
                client.global_world.destroy()

if __name__ == '__main__':
    unittest.main()