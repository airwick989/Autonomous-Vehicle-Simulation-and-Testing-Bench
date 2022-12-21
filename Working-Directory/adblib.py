import subprocess
import time

def connect():
    #subprocess.call(["adb","connect","10.160.5.106"])
    device = subprocess.Popen("adb shell", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return device

def volume_up():
    global device
    device.stdin.write(("input keyevent 24 \n").encode())
    device.stdin.flush()
    return True

def volume_down():
    global device
    device.stdin.write(("input keyevent 25 \n").encode())
    device.stdin.flush()
    #device.shell('input keyevent 25')
    return True

def play_pause():
    global device
    device.stdin.write(("input keyevent 85 \n").encode())
    device.stdin.flush()
    #device.shell('input keyevent 85')
    return True

def next():
    global device
    device.stdin.write(("input keyevent 87 \n").encode())
    device.stdin.flush()
    #device.shell('input keyevent 87')
    return True

def previous():
    global device
    device.stdin.write(("input keyevent 88 \n").encode())
    device.stdin.flush()
    #device.shell('input keyevent 88')
    return True

def back():
    global device
    device.stdin.write(("input keyevent 4 \n").encode())
    device.stdin.flush()
    #device.shell('input keyevent 4')
    return True

def recent_apps():
    global device
    device.stdin.write(("input keyevent KEYCODE_APP_SWITCH \n").encode())
    device.stdin.flush()
    #device.shell('input keyevent KEYCODE_APP_SWITCH')
    return True

def launch_app(package_name):
    command = f'monkey -p {package_name} 1'
    device.stdin.write((command+"\n").encode())
    device.stdin.flush()
    #device.shell(command)

def home():
    global device
    device.stdin.write(("input keyevent 3 \n").encode())
    device.stdin.flush()
#    device.shell('input keyevent 3')
    return True


########################################################################################################################################################################################


device = connect()
#launch_app(package_name='com.soundcloud.android')   #package:com.android.chrome

#adb shell pm list packages

# for i in range(0,6):    #Turn the volum up 5 ticks, 1 is to trigger the volume controls
#     volume_up(device)
#     time.sleep(0.1)

# time.sleep(2)

# for i in range(0,6):
#     volume_down(device)
#     time.sleep(0.1)
