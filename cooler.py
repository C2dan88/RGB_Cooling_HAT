import Adafruit_GPIO.I2C as I2C

import time
import os
import smbus
bus = smbus.SMBus(1)

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import psutil

hat_addr = 0x0d
rgb_effect_reg = 0x04
fan_reg = 0x08

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit 
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/home/pi/RGB_Cooling_HAT/Minecraftia.ttf', 8)

def setFanSpeed(speed):
    bus.write_byte_data(hat_addr, fan_reg, speed&0xff)
    # if speed == 0x01:
    #    speed = 10
    # print(f"Setting fan speed to: {speed}0%")


RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
ORANGE = (255, 100, 0)
BLACK  = (0, 0, 0)


def setRGB(r, g, b):
    # print(f"Setting rgb: {(r, g, b)}")  
    bus.write_byte_data(hat_addr, 0x00, 0xff)
    bus.write_byte_data(hat_addr, 0x01, r&0xff)
    bus.write_byte_data(hat_addr, 0x02, g&0xff)
    bus.write_byte_data(hat_addr, 0x03, b&0xff)


def getCpuLoad():
    return 'CPU: ' + str(int(psutil.cpu_percent())) + '%'


def getCpuTemp():
    cmd = os.popen('vcgencmd measure_temp').readline()
    cpu_temp = cmd.replace("temp=","").replace("'C\n","")
    return float(cpu_temp)


def setOLEDshow(cpu_temp, fan_speed):
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    CPU = getCpuLoad()

    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True)

    draw.text((x, top), str(CPU), font=font, fill=255)
    draw.text((x+60, top), 'Temp: ' + str(cpu_temp) + 'C', font=font, fill=255)
    
    if fan_speed == 0x01:
        fan_speed = 10
    draw.text((x, top+20), f"Fan: {int(fan_speed*10)}%",  font=font, fill=255)
    
    draw.text((x, top+10), 'RAM: ' + str(int(psutil.virtual_memory().percent)) + '%',  font=font, fill=255)

    #draw.text((x, top+20), "IP: " + str(IP.decode('UTF-8')),  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()


updateInterval = 10 # time in seconds to update fan/rgb 

start_time = time.time()

prev_time = start_time - 10
prev_fanspeed = 0
prev_rgb = BLACK

while True:
    
    cpu_temp = getCpuTemp()
    
    if cpu_temp <= 40:
        fanspeed = 0x03 # 30% fan speed
        rgb_color = BLUE
    elif cpu_temp > 40 and cpu_temp <= 60:
        fanspeed = 0x05 # 50% fan speed
        rgb_color = GREEN
    elif cpu_temp > 60 and cpu_temp <= 80:
        fanspeed = 0x07 # 70% fan speed
        rgb_color = ORANGE
    elif cpu_temp > 80:
        fanspeed = 0x01 # 100% fan speed
        rgb_color = RED
        
    # update fan/rgb affter interval passes
    end_time = time.time()
    if (end_time - prev_time) >= updateInterval:
        if fanspeed != prev_fanspeed:
            setFanSpeed(fanspeed)
            prev_fanspeed = fanspeed

        if rgb_color != prev_rgb:
            setRGB(*rgb_color)
            prev_rgb = rgb_color
            
        prev_time = end_time
            
    setOLEDshow(cpu_temp, fanspeed)
    time.sleep(1)
