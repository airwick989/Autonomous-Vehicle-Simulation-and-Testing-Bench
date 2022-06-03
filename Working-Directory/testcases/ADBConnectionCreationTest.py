import unittest

from subprocess import check_output, CalledProcessError
try:
    adb_ouput = check_output(["adb", "devices"])
except CalledProcessError as e:
    print(f"error: {e.returncode}")

connection = str(adb_ouput)
connectionStripped = connection.replace("\\t","+")
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
