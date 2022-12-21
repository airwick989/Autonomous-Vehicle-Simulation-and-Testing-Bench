import serial.tools.list_ports
import unittest

allports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
ports = []
for port in allports:
    ports.append(port[0])

class TestSerialConnection(unittest.TestCase):
    
    def test_addresses(self):
        known_addresses = ['/dev/ttyACM0', '/dev/ttyACM1']
        self.assertTrue(all(address in ports for address in known_addresses))

if __name__ == '__main__':
    unittest.main()