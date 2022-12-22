
import adbutils

adb = adbutils.AdbClient(host="10.160.7.48", port=5555)
print(adb.device_list())