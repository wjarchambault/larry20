import os
import time
import datetime
import random
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)
cs.direction = digitalio.Direction.INPUT

reset = digitalio.DigitalInOut(board.D20)
reset.direction = digitalio.Direction.OUTPUT
strobe = digitalio.DigitalInOut(board.D21)
strobe.direction = digitalio.Direction.OUTPUT

mEnable = digitalio.DigitalInOut(board.D13)
mEnable.direction = digitalio.Direction.OUTPUT
in1 = digitalio.DigitalInOut(board.D4)
in1.direction = digitalio.Direction.OUTPUT
in2 = digitalio.DigitalInOut(board.D17)
in2.direction = digitalio.Direction.OUTPUT
in3 = digitalio.DigitalInOut(board.D19)
in3.direction = digitalio.Direction.OUTPUT
in4 = digitalio.DigitalInOut(board.D26)
in4.direction = digitalio.Direction.OUTPUT

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# block character
#blockChar = u'\u2591'+u'\u2591'
blockChar = u'\u2591' * 2

def open_mouth():
   in1.value = True
   in2.value = False

def close_mouth():
   in1.value = False
   in2.value = True

def relax_mouth():
   in1.value = False
   in2.value = False

def open_lids():
   in3.value = False
   in4.value = True

def close_lids():
   in3.value = True
   in4.value = False

def relax_lids():
   in3.value = False
   in4.value = False

# create analog input channels
chan0 = AnalogIn(mcp, MCP.P0)

#print("\nChan0", dir(chan0))

# Init spectrum analyzer
strobe.value = False
time.sleep(0.01)
reset.value = True
time.sleep(0.01)
strobe.value = True
time.sleep(0.01)
strobe.value = False
time.sleep(0.01)
reset.value = False
time.sleep(0.01)

# Init motor driver
mEnable.value = True
try_count = 0
no_sound = True

try:
    a = datetime.datetime.now()
    random_num = random.randint(0,9)
    lids_closed = False
    random_blink = False
    open_lids()    
    time.sleep(1)
    while True:
        b = datetime.datetime.now()
        c = b - a
        tens, ones = divmod(a.second, 10)
        if not random_blink:
           if ones == random_num:
              close_lids()
              random_blink = True
              lids_closed = True
        if c.microseconds > 455000:
           a = datetime.datetime.now()
           if lids_closed:
              open_lids()
              random_blink = False
              lids_closed = False
              random_num = random.randint(0,9)
           else:
              relax_lids()
        try_count = try_count + 1
        chanLeft = []
        for freq in range(4):
            strobe.value = True
            strobe.value = False
            chanLeft.append(int(chan0.voltage))
        sumLeft = sum(chanLeft)
        if sumLeft > 0:
#            print(blockChar * sumLeft)
            no_sound = False
            open_mouth()
        else:
            if no_sound:
               relax_mouth()
            else:
               close_mouth()
#            print("\n")
        if try_count > 250:
            no_sound = True
            try_count=0
except KeyboardInterrupt:
    print('Keyboard Interrupt')
    mEnable.value = False
    relax_mouth()
    relax_lids()
