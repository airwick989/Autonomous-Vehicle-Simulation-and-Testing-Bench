import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')
testingFlag = 24

import testbed as client
class TestADBCommand(unittest.TestCase):
    def setUp(self):
        self.longMessage=False

    def test_command(self):
        for i in range(6, 14):
            with self.subTest(i = i):
                client.main(23)
                if i == 13:
                    self.assertTrue(client.global_controller.parse_events(client.global_world, client.global_clock, testingFlag, 2))
                else:
                    self.assertTrue(client.global_controller.parse_events(client.global_world, client.global_clock, testingFlag, i))
                client.global_world.destroy()

if __name__ == '__main__':
    unittest.main()