import time

from ppadb.client import Client as AdbClient

def connect():
    client = AdbClient(host="10.160.7.48", port=5555) # Default is "127.0.0.1" and 5037
    print(client)
    devices = client.devices()
    print(devices)
    if len(devices) == 0:
        print('No devices')
        quit()

    device = devices[0]

    print(f'Connected to device: {device}\nClient: {client}\n\n')

    return device, client

def volume_up():
    global device
    device.shell('input keyevent 24')
    return True

def volume_down():
    global device
    device.shell('input keyevent 25')
    return True

def play_pause():
    global device
    device.shell('input keyevent 85')
    return True

def next():
    global device
    device.shell('input keyevent 87')
    return True

def previous():
    global device
    device.shell('input keyevent 88')
    return True

def back():
    global device
    device.shell('input keyevent 4')
    return True

def recent_apps():
    global device
    device.shell('input keyevent KEYCODE_APP_SWITCH')
    return True

def launch_app(package_name):
    command = f'monkey -p {package_name} 1'
    device.shell(command)

def home():
    global device
    device.shell('input keyevent 3')
    return True


########################################################################################################################################################################################


device, client = connect()

#launch_app(package_name='com.soundcloud.android')   #package:com.android.chrome

#adb shell pm list packages

# for i in range(0,6):    #Turn the volum up 5 ticks, 1 is to trigger the volume controls
#     volume_up(device)
#     time.sleep(0.1)

# time.sleep(2)

# for i in range(0,6):
#     volume_down(device)
#     time.sleep(0.1)
