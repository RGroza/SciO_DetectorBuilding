import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import I2C_LCD_driver
lcd= I2C_LCD_driver.lcd()

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}".format('raw', 'v'))
values = []
try:
    for i in range(50):
        u = chan.voltage
        values.append() = u
        print("{:>5}\t{:>5}".format(chan.value, chan.voltage))
        lcd.lcd_clear()
        lcd.lcd_display_string('Voltage: ' + str(round(u, 8)) + 'V', 1)
        time.sleep(0.2)
    def Average(list):
        return sum(list)/len(list)
    avg = Average(values)
    lcd.lcd_display_string('Average voltage: ' + str(round(avg, 8)) + 'V', 2)
    print(avg)
except KeyboardInterrupt:
    lcd.lcd_clear()
