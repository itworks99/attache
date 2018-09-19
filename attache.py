##import RPi.GPIO as GPIO
##import Adafruit_GPIO.SPI as SPI
##import Adafruit_SSD1306

import time
import os
# ------------------------------------------
# Pi settings:
# ------------------------------------------
# Input pins:
L_pin = 13 
R_pin = 5 
C_pin = 19 
U_pin = 6 
D_pin = 26 
A_pin = 22 
B_pin = 27
# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0
# ------------------------------------------
# Attache configuration
# ------------------------------------------
configFile = "/etc/attache.conf"
mountsLocation = "/proc/mounts"
mountedDeviceMask = "/dev/sd"
clamavLocation = "/usr/bin/clambc"

mountedVolumes = []
mountedVolumesOnStart = []

configFilePresent = None
clamavPresent = None
# ------------------------------------------
# Functions
# ------------------------------------------
def checkMountedDevices(outputArray):
  mountedDevices = open(mountsLocation)
  for mountedDevice in mountedDevices:
    if mountedDevice.startswith(mountedDeviceMask):
        outputArray.append(mountedDevice.split(' ')[0])
  mountedDevices.close()
  return outputArray

def checkFilePresence(location):
  if os.path.exists(location):
    filePresent = True
  else:
    filePresent = False
  return filePresent
# ------------------------------------------
# INIT
# ------------------------------------------
# ------------------------------------------
# Pi init:
# ------------------------------------------
#GPIO.setmode(GPIO.BCM) 

#GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# 128x64 display with hardware I2C:
##disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
#disp.begin()

# Clear display.
#disp.clear()
#disp.display()
# ------------------------------------------
# ATTACHE INIT
# ------------------------------------------
configFilePresent = checkFilePresence(configFile)
clamavPresent = checkFilePresence(clamavLocation)
checkMountedDevices(mountedVolumesOnStart)
print(sorted(mountedVolumesOnStart))
# ------------------------------------------
# Main loop
# ------------------------------------------
while True:
  checkMountedDevices(mountedVolumes)