from git import Repo
import git
import subprocess
from pathlib import Path
import os
import shutil
file = open("C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client\\CICD-Framework-Test-Cases\\increment.txt", "r")
currentVal = file.read()
newDirectory = "C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client\\CICD-Framework-Test-Cases\\Build" + str(currentVal)
if not os.path.exists(newDirectory):
    os.makedirs(newDirectory)
Repo.clone_from('https://github.com/Tahaa17/capstone-app', newDirectory)
file = open("C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client\\CICD-Framework-Test-Cases\\increment.txt", "w")


os.chdir(newDirectory+'\\MusicPlayer')
subprocess.call('gradlew assembleDebug',shell=True)
f= newDirectory + "\\MusicPlayer\\app\\build\\outputs\\apk\\debug\\app-debug.apk"
subprocess.call("adb install -r "+f,shell=True)
newVal = int(currentVal) + 1
file.write(str(newVal))
file = open("C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client\\CICD-Framework-Test-Cases\\fileUploaded.txt", "w")
toWrite = str(subprocess.check_output("aapt dump badging "+f+" | findstr -n \"package: name\" | findstr \"1:\""))
toWrite.strip()
toWriteArray = toWrite.split("\'")

file.write(toWriteArray[1])
file.close()

