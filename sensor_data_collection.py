from time import sleep
import smbus
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import os

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

   # display string on lcd screen
   def lcd_display_string(self, string, line=1):
      if line == 1:
         self.lcd_write(0x80)
      elif line == 2:
         self.lcd_write(0xC0)
      elif line == 3:
         self.lcd_write(0x94)
      elif line == 4:
         self.lcd_write(0xD4)
      else:
         raise Exception("Line parameter must be 1, 2, 3, or 4.")
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

def average(values):
   return sum(values) / len(values)

def open_file():
   file_list = []
   for file in os.listdir("data"):
       if file.endswith(".txt") and file.startswith("sensor_data"):
           file_list.append(file)
   file_iter = str(len(file_list)) if len(file_list) > 0 else ""
   sensor_data = open(f"data/sensor_data{file_iter}.txt", "a")
   sensor_data.write("Temp (" + u'\N{DEGREE SIGN}' + "C)" + "    Avg V")
   print("File Opened!")
   return sensor_data

sensor_data = open_file()

values = []
try:
   while True:
      tempStr = round(float(input("Input Temp (" + u'\N{DEGREE SIGN}' + "C) ")), 1)

      print('\n{:>5}\t{:>13}'.format('Raw', 'Voltage'))
      for i in range(50):
         v = chan.voltage
         values.append(v)

         print('{:>5}\t{:>5}'.format(chan.value, chan.voltage))

         if i % 5 == 0:
            display.lcd_display_string(f"Voltage: {str(round(v, 8))} V", 1)
            sleep(0.2)
            display.lcd_clear()

      avg = average(values)
      rounded_avg = round(avg, 8)

      display.lcd_display_string(f"Inputted Temp: {tempStr}")
      display.lcd_display_string("Average voltage: ", 2)
      display.lcd_display_string(f"{str(rounded_avg)} V", 3)

      sensor_data.write(f"\n{tempStr}         {rounded_avg}")

      print(f"Average voltage: {str(avg)} V\n")
      values = []
except KeyboardInterrupt:
   display.lcd_clear()
