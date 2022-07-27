import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')

import testbed_modified as client
class TestHandBrake(unittest.TestCase):
    def test_handbrake(self):
        client.main(22)
        self.assertLess(client.get_speed(client.global_world, 0),1,msg="FAILURE! The hand brake is not working as intended!")
    def test_destroy(self):
        if (client.global_world and client.global_world.recording_enabled):
            client.global_client.stop_recorder()
        if client.global_world is not None:
            client.global_world.destroy()

if __name__ == '__main__':
    unittest.main()