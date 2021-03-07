import os
import time
import datetime
import random
import busio
import digitalio
import board
import pwmio
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

m1Enable = digitalio.DigitalInOut(board.D13)
m1Enable.direction = digitalio.Direction.OUTPUT
m2Enable = pwmio.PWMOut(board.D6)

in1 = digitalio.DigitalInOut(board.D4)
in1.direction = digitalio.Direction.OUTPUT
in2 = digitalio.DigitalInOut(board.D17)
in2.direction = digitalio.Direction.OUTPUT
in3 = digitalio.DigitalInOut(board.D19)
in3.direction = digitalio.Direction.OUTPUT
in4 = digitalio.DigitalInOut(board.D26)
in4.direction = digitalio.Direction.OUTPUT

high_value = 33000
low_value = 22000

low_lids_value = 13500
high_lids_value = 33500

#PWM duty cycle choices
duty_cycle_100 = 65535
duty_cycle_75 = 49152
duty_cycle_50 = 32768
duty_cycle_25 = 16384
duty_cycle_0 = 0

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# block character
#blockChar = u'\u2591'+u'\u2591'
blockChar = u'\u2591' * 2

def open_mouth(mouth_value):
   if mouth_value < high_value:
#       print("Opening mouth:", mouth_value)
       in1.value = True
       in2.value = False
   else:
#       print("Open Mouth Limit reached", mouth_value)
       in1.value = False
       in2.value = False

def close_mouth(mouth_value):
   if mouth_value > low_value+3000:
#       print("Closing mouth:", mouth_value)
       in1.value = False
       in2.value = True
   else:
#       print("Close mouth Limit reached:", mouth_value)
       in1.value = False
       in2.value = False

def relax_mouth():
   in1.value = False
   in2.value = False

def open_lids(lids_value):
   global random_blink
   #print("Open lids", lids_value)
   if lids_value < high_lids_value:
       in3.value = False
       in4.value = True
   else:
       m2Enable.duty_cycle = duty_cycle_0
       random_blink = False
       in3.value = False
       in4.value = False

def close_lids(lids_value):
   global close_the_lids
   #print("Close lids", lids_value)
   if lids_value > low_lids_value:
       in3.value = True
       in4.value = False
   else:
       close_the_lids = False
       in3.value = False
       in4.value = False

def relax_lids():
   in3.value = False
   in4.value = False

# create analog input channels
chan0 = AnalogIn(mcp, MCP.P0)
chan1 = AnalogIn(mcp, MCP.P1)
chan2 = AnalogIn(mcp, MCP.P2)

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
m1Enable.value = True
m2Enable.duty_cycle = duty_cycle_50

try:
    close_the_lids = False
    random_blink = False
    lids_value = chan2.value
    while lids_value < high_lids_value:
        lids_value = chan2.value
        open_lids(lids_value)
    in3.value = False
    in4.value = False
    m2Enable.duty_cycle = duty_cycle_0
    blink_now = [random.randrange(1, 60, 1) for i in range(14)]
    while True:
        a = datetime.datetime.now()
        if not random_blink:
            if a.second in blink_now:
                m2Enable.duty_cycle = duty_cycle_50
                random_blink = True
                close_the_lids = True
#                print("Random eye blink activated...", a.second)
        lids_value = chan2.value
        if close_the_lids:
            close_lids(lids_value)
        else:
            open_lids(lids_value)
        chanLeft = []
        for freq in range(4):
            strobe.value = True
            strobe.value = False
            chanLeft.append(int(chan0.voltage))
#        sumLeft = sum(chanLeft)
        sumLeft = chanLeft[0]+chanLeft[2]+chanLeft[3]
        mouth_value = chan1.value
        if sumLeft > 0:
#            print(blockChar * sumLeft)
            open_mouth(mouth_value)
        else:
            close_mouth(mouth_value)
except KeyboardInterrupt:
    print('Keyboard Interrupt')
    m1Enable.value = False
    m2Enable.value = False
    relax_mouth()
    relax_lids()
