import sys
import unittest

sys.path.insert(1,'C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client')

import client_MODIFIED as client
class TestGearShifterKit(unittest.TestCase):
    def test_brake_input(self):
        client.main(4)
        print(client.get_speed())
        self.assertLess(client.get_speed(),1, "FAILURE! Gear shifter is in park! Car speed should be less than 0!")
if __name__ == '__main__':
    unittest.main()


