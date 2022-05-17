import sys
import unittest

sys.path.insert(1,'C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client')

import client_MODIFIED as client
class TestSteeringWheelKit(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_brake_input(self):
        client.main(2)
        print(client.get_speed())
        self.assertLess(client.get_speed(),1,"FAILURE! Brakes are not working as intended!")
if __name__ == '__main__':
    unittest.main()


