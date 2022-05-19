import sys
import unittest

sys.path.insert(1,'C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client')

import client_MODIFIED as client
class TestSteeringWheelKit(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_acceleration_input(self):
        client.main(1)
        self.assertGreater(client.get_speed(),1,msg="FAILURE! Acceleration is not working as intended!")
if __name__ == '__main__':
    unittest.main()


