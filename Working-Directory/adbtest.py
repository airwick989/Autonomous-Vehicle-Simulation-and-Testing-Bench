import time

from ppadb.client import Client as AdbClient

def connect():
    client = AdbClient(host="127.0.0.1", port=5037) # Default is "127.0.0.1" and 5037

    devices = client.devices()

    if len(devices) == 0:
        print('No devices')
        quit()

    device = devices[0]

    print(f'Connected to device: {device}\nClient: {client}\n\n')

    return device, client

def volume_up(device):
    device.shell('input keyevent 24')

def volume_down(device):
    device.shell('input keyevent 25')

def launch_app(package_name):
    command = f'monkey -p {package_name} 1'
    device.shell(command)


########################################################################################################################################################################################


device, client = connect()

#print(device.shell('adb shell pm list packages'))
launch_app(package_name='com.android.chrome')   #package:com.android.chrome

# for i in range(0,6):    #Turn the volum up 5 ticks, 1 is to trigger the volume controls
#     volume_up(device)
#     time.sleep(0.1)

# time.sleep(2)

# for i in range(0,6):
#     volume_down(device)
#     time.sleep(0.1)