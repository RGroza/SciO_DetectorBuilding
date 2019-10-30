import random
import time
import I2C_LCD_driver
lcd = I2C_LCD_driver.lcd()
print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
print('-'*37)
while True:
    randomNum = random.randrange(0,32767)
    values = [randomNum,0,0,0]
    print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
    u = round(values[0]*(4.096/32767),3)
    lcd.lcd_clear()
    lcd.lcd_display_string('Voltage: ' + str(u) + 'V', 1)
    time.sleep(2)
