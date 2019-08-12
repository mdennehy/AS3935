#!/usr/bin/python3

import time
import spidev
import RPi.GPIO as GPIO
import pprint as pp


# lighning detection interrupt handler
def handle_interrupt(channel):
    print("interrupt!")
    pp.pprint(spi.xfer2([0x40]))
    time.sleep(0.003)


# rig chip
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT) # SI
GPIO.setup(6, GPIO.IN) # IRQ
GPIO.setup(13, GPIO.OUT) # EN-V

GPIO.output(5, 0) # Select SPI on sensor
GPIO.output(13, 0) # Select on-sensor voltage regulator

# register interrupt handler
GPIO.add_event_detect(6, GPIO.RISING, callback=handle_interrupt)

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 0

# Enable SPI
spi = spidev.SpiDev()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)

# Set SPI speed and mode
spi.max_speed_hz = 488000 #not 500khz to avoid noise and less than 2Mhz
spi.mode = 0b01

# Initialise sensor
print("reset sensor registers")
spi.xfer2([0x3C, 0x96])
time.sleep(0.003)

# Sensor self-calibrate
print("sensor self-calibrate")
spi.xfer2([0x3D, 0x96])
time.sleep(0.6)

# Sensor enable interrupt
print("sensor enable interrupt")
spi.xfer2([0x08, 0xDF])
time.sleep(0.2)


# Set up to read all registers
cmd = 0x40 # read
addr = 0x00

# Turn on one segment of each character to show that we can
# address all of the segments
# while addr < 0x32:
while addr < 0x02:
    msg = [cmd|addr]

    # print("{:b} | {:b} => {:b}".format(cmd, addr, msg))
    print("cmd:    0x{0:02x}  0b{0:08b}".format(cmd))
    print("addr:   0x{0:02x}  0b{0:08b}".format(addr))
    print("msg:    0x{0:02x}  0b{0:08b}".format(msg[0]))

    result = spi.xfer2(msg)

    print("result: 0x{0:02x}  0b{0:08b}".format(result[0]))
    print("-----------------")
    # print("result: {:x}".format(result[0]))
    # print(result)

    # Increment to next segment in each character
    addr += 0x01

    time.sleep(0.5)

while True:
    time.sleep(10)
    print(".")
