import sys
import unittest

sys.path.insert(1,'/home/rtemsoft/Desktop/CARLA-Simulation-Bench/Working-Directory')

import testbed as client
class TestSteeringWheelKit(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_acceleration_input(self):
        client.main(1)
        self.assertGreater(client.get_speed(client.global_world, 0),1,msg="FAILURE! Acceleration is not working as intended!")
    def test_destroy(self):
        if (client.global_world and client.global_world.recording_enabled):
            client.global_client.stop_recorder()
        if client.global_world is not None:
            client.global_world.destroy()

if __name__ == '__main__':
    unittest.main()