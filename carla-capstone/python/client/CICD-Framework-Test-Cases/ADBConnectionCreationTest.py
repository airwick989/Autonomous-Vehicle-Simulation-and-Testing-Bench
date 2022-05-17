import sys
import getopt
import subprocess
import unittest
connection = subprocess.check_output("adb devices").strip()
connectionStripped = str(connection).replace("\\t","+")
class TestADB(unittest.TestCase):
    def setUp(self):
        self.longMessage=False
    def test_creation_of_connection(self):
        connectionCreated = False
        if("SGWOOFVOO7NJRO7H+device" in str(connectionStripped)):
            print("ADB connection established!")
            connectionCreated = True
        elif("SGWOOFVOO7NJRO7H+offline" in str(connectionStripped)):
            connectionCreated = False
        else:
            connectionCreated = False
        self.assertTrue(connectionCreated,msg="FAILURE! ADB connection could not be established!")

if __name__ == '__main__':
    unittest.main()
