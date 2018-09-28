import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import sys,time,os,pyclamd

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
P_WAIT = 0

configFile = "/etc/attache.conf"
mountsLocation = "/proc/mounts"
mountedDeviceMask = "/dev/sd"

virusFoundMarker = 'FOUND'

repairCommmand = "clamdscan --remove=yes "
repairReport = " > /tmp/report.tmp"

clamavReport = []

fontName = "visitor1.ttf"
fontSizeSmall = 10
fontSizeLarge = 20

secondsToWait = 2

mountedVolumes = []
mountedVolumesOnStart = []
volumesToScan = []
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

def progressDot(x,y):
    xyDot = [[0, 0], [1, 0], [2, 0], [3, 0], [3, 1], [3, 2], [3, 3], [2, 3], [1, 3], [0, 3], [0, 2], [0, 1]]
    xSize = 4
    ySize = 2
    prevItem = [0,1]
    for item in xyDot:
        draw.rectangle((x*item[0], y*item[1],x*item[0]+xSize, y*item[1]+ySize),outline=255, fill=255)
        draw.rectangle((x*prevItem[0], y*prevItem[1], x*prevItem[0] + xSize, y*prevItem[1] + ySize), outline=0, fill=0)        
        disp.image(image)
        disp.display()
        time.sleep(secondsToWait)
        prevItem = item
    return
                

def scanForViruses(volumeToScan):
    clear1306()
    printLarge1306(0, 0, 'Scanning')
    printSmall1306(0, 14, volumeToScan.replace('/media/',''))
    scanOutput = str(clamavDaemon.contscan_file(str(volumeToScan)))
    foundcounter = 0
    last_found = -1  # Begin at -1 so the next position to search from is 0
    while True:
        last_found = scanOutput.find(virusFoundMarker, last_found + 1)
        if last_found == -1:  
            break  # All occurrences have been found
        else:
            foundcounter += 1
            clear1306()
    printLarge1306(0, 0, 'found '+ str(foundcounter))
    printLarge1306(0, 14, 'viruses')        
    
    if foundcounter > 0:
        printLarge1306(0, 28, 'cleaning...')
        print (repairCommmand + volumeToScan + repairReport)
        os.spawnl(P_WAIT, (repairCommmand + volumeToScan + repairReport))
    return True

def scanfile(file):
    # Call libclamav thought pyclamav
    try:
        ret=pyclamd.scanfile(file)
    except (ValueError, e):
        print ('** A problem as occured :', e, '("'+file+'")')
        return None
    except (TypeError, e):
        print ('** A problem as occured :', e, '("'+file+'")')
        return None
    else:
        # Check return tupple
        if ret[0]==0:
            print (file, 'is not infected')
            return True
        elif ret[0]==1:
            print (file, 'is infected with', ret[1])
            return False

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

progressDot(2,2)

# ------------------------------------------
# Main loop
# ------------------------------------------
while True:
    print(clamavDaemon.stats().split()[0])
#    time.sleep(secondsToWait)
    checkMountedDevices(mountedVolumes)
    if mountedVolumes > mountedVolumesOnStart:
        volumesToScan.append((set(mountedVolumes) - set(mountedVolumesOnStart)))
        print (volumesToScan)
        for volumeRecord in volumesToScan:
            volumeToScan = str(volumeRecord).replace("[{'", "").replace("'}]", "")

            scanForViruses(volumeToScan)        
        
        volumesToScan.clear()

        printLarge1306(0, 42, 'done! ')

        mountedVolumes.clear()
        mountedVolumesOnStart =  mountedVolumes
    else:
        mountedVolumes.clear()