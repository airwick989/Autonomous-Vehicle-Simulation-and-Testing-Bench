import sys
import getopt
import subprocess
import unittest
brakeMethod = "Vehicle.brake.press()"
invocation = str(subprocess.check_output("adb logcat -d | FINDSTR Vehicle.brake.press()"))
if brakeMethod in invocation:
    print("I AM A MALICIOUS ATTACK ON THE CAR")
    subprocess.call('taskkill /IM CarlaUE4.exe /F',shell=True)
