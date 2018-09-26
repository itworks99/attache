import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import time
import os
import pyclamd

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Buttons settings:
L_pin = 13  # Input pins:
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

# Attache configuration
configFile = "/etc/attache.conf"
mountsLocation = "/proc/mounts"
mountedDeviceMask = "/dev/sd"

fontName = "visitor1.ttf"
fontSizeSmall = 10
fontSizeLarge = 20

secondsToWait = 3

mountedVolumes = []
mountedVolumesOnStart = []
scanVolumes = []
scanOutput = []

configFilePresent = None
clamavPresent = None

# Functions
def checkMountedDevices(outputArray):
    mountedDevices = open(mountsLocation)
    for mountedDevice in mountedDevices:
        if mountedDevice.startswith(mountedDeviceMask):
            outputArray.append((mountedDevice.split(" ")[1]).replace("\\040", " "))
    mountedDevices.close()
    return outputArray


def checkFilePresence(location):
    if os.path.exists(location):
        filePresent = True
    else:
        filePresent = False
    return filePresent

def printSmall1306(x, y, text):
    font = ImageFont.truetype(fontName, fontSizeSmall)
    draw.text((x, y), text, font=font, fill=255)
    disp.image(image)
    disp.display()
    return

def printLarge1306(x, y, text):
    font = ImageFont.truetype(fontName, fontSizeLarge)
    draw.text((x, y), text, font=font, fill=255)
    disp.image(image)
    disp.display()
    return

def clear1306():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)  # Draw a black filled box to clear the image
    disp.display()
    return

# ------------------------------------------
# INIT
# ------------------------------------------
# Pi init:
GPIO.setmode(GPIO.BCM)
GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)  # 128x64 display with hardware I2C:
disp.begin()  # Initialize library.
disp.clear()  # Clear display.
disp.display()
width = disp.width  # Create blank image for drawing.
height = disp.height
image = Image.new(
    "1", (width, height)
)  # Make sure to create image with mode '1' for 1-bit color.
draw = ImageDraw.Draw(image)  # Get drawing object to draw on image.
draw.rectangle(
    (0, 0, width, height), outline=0, fill=0
)  # Draw a black filled box to clear the image.
padding = -2
top = padding
bottom = height - padding
x = 0
y = 0

# ------------------------------------------
# ATTACHE INIT
# ------------------------------------------
printLarge1306(0, 0, "loading...")
clamavDaemon = pyclamd.ClamdAgnostic()
# configFilePresent = checkFilePresence(configFile)
printSmall1306(0, 14, str(clamavDaemon.version()))
checkMountedDevices(mountedVolumesOnStart)
printSmall1306(0, 22, str(sorted(mountedVolumesOnStart)))
# TODO: Add check wheter ClamAV database is loaded into memory and daemon is ready
printLarge1306(0, 30, "ok.")
time.sleep(secondsToWait)
clear1306()
printLarge1306(0, 0, "Ready")
# ------------------------------------------
# Main loop
# ------------------------------------------
while True:
    checkMountedDevices(mountedVolumes)
    if mountedVolumes != mountedVolumesOnStart:
        scanVolumes.append((set(mountedVolumes) - set(mountedVolumesOnStart)))
        scanVolume = str(scanVolumes).replace("[{'", "").replace("'}]", "")
        print(str(scanVolume))
        scanOutput = str(clamavDaemon.contscan_file(str(scanVolume)))
        if scanOutput.find("ERROR"):
            print("ERROR:")
            print("------")
            print(scanOutput)
        mountedVolumes.clear()
        break
    else:
        mountedVolumes.clear()
