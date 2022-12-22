import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory-v2')

import testbed_modified as client
class TestGearShifterKit(unittest.TestCase):
    def test_brake_input(self):
        client.main(4)
        self.assertLess(client.get_speed(client.global_world, 0),1, "FAILURE! Gear shifter is in park! Car speed should be less than 0!")
    def test_destroy(self):
        if (client.global_world and client.global_world.recording_enabled):
            client.global_client.stop_recorder()
        if client.global_world is not None:
            client.global_world.destroy()

if __name__ == '__main__':
    unittest.main()