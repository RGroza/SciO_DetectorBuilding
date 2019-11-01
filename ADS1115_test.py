from time import sleep
import smbus
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

address = 0x27

class i2c_device:
   def __init__(self, addr, port=1):
      self.addr = addr
      self.bus = smbus.SMBus(port)

# Write a single command
   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)

class lcd:
   def __init__(self):
      self.lcd_device = i2c_device(address)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x02)
      self.lcd_write(0x20 | 0x08 | 0x00 | 0x00)
      self.lcd_write(0x08 | 0x04)
      self.lcd_write(0x01)
      self.lcd_write(0x04 | 0x02)
      sleep(0.2)

   def lcd_strobe(self, data):
      self.lcd_device.write_cmd(data | 0b00000100 | 0x08)
      sleep(.0005)
      self.lcd_device.write_cmd(((data & ~0b00000100) | 0x08))
      sleep(.0001)

   def lcd_write_four_bits(self, data):
      self.lcd_device.write_cmd(data | 0x08)
      self.lcd_strobe(data)

   # write a command to lcd
   def lcd_write(self, cmd, mode=0):
      self.lcd_write_four_bits(mode | (cmd & 0xF0))
      self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

   # put string function with optional char positioning
   def lcd_display_string(self, string, line=1, pos=0):
    if line == 1:
      pos_new = pos
    elif line == 2:
      pos_new = 0x40 + pos
    elif line == 3:
      pos_new = 0x14 + pos
    elif line == 4:
      pos_new = 0x54 + pos
    self.lcd_write(0x80 + pos_new)
    for char in string:
      self.lcd_write(ord(char), 0b00000001)

   # clear lcd and set to home
   def lcd_clear(self):
      self.lcd_write(0x01)
      self.lcd_write(0x02)

display = lcd()

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

print('{:>5}\t{:>13}'.format('Raw', 'Voltage'))
values = []
def average(list):
    return sum(list)/len(list)
try:
    for i in range(50):
        u = chan.voltage
        values.append(u)
        print('{:>5}\t{:>5}'.format(chan.value, chan.voltage))
        display.lcd_display_string('Voltage: ' + str(round(u, 8)) + 'V', 1)
        sleep(0.2)
        display.lcd_clear()
    avg = average(values)
    display.lcd_display_string('Average voltage: ', 1)
    display.lcd_display_string(str(round(avg, 8)) + 'V', 2)
    print('Average voltage: ' + str(avg) + 'V')
except KeyboardInterrupt:
    display.lcd_clear()
