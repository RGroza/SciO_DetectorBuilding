import RPi.GPIO as GPIO
from time import sleep
from random import random
import I2C_LCD_driver

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

redLED = 16
greenLED = 10
blueLED = 12

GPIO.setup(redLED, GPIO.OUT, initial=GPIO.LOW) # red LED
GPIO.setup(greenLED, GPIO.OUT, initial=GPIO.LOW) # green LED
GPIO.setup(blueLED, GPIO.OUT, initial=GPIO.LOW) # blue LED

r = GPIO.PWM(redLED, 100)
r.start(0)
g = GPIO.PWM(greenLED, 100)
g.start(0)
b = GPIO.PWM(blueLED, 100)
b.start(0)

max_bright = 100 # max brightness of PWM cycle
pwm_delay = .005 # delay between cycles
pulses = 2

degree_sign= u'\N{DEGREE SIGN}'

mylcd = I2C_LCD_driver.lcd()

try:
    while True:
        randTemp = round(75*random(), 1)
        if randTemp < 25:
            print(str(randTemp) + degree_sign + "C: low temp")
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Temp: " + str(randTemp) + chr(223) + "C (low)", 1)
            for i in range(pulses):
                for n in range(max_bright):
                    b.ChangeDutyCycle(n+1)
                    sleep(pwm_delay)
                for n in range(max_bright):
                    b.ChangeDutyCycle(max_bright - (n+1))
                    sleep(pwm_delay)
        elif randTemp < 50:
            print(str(randTemp) + degree_sign + "C: mid temp")
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Temp: " + str(randTemp) + chr(223) + "C (mid)", 1)
            for i in range(pulses):
                for n in range(max_bright):
                    g.ChangeDutyCycle(n+1)
                    sleep(pwm_delay)
                for n in range(max_bright):
                    g.ChangeDutyCycle(max_bright - (n+1))
                    sleep(pwm_delay)
        else:
            print(str(randTemp) + degree_sign + "C: high temp")
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Temp: " + str(randTemp) + chr(223) + "C (high)", 1)
            for i in range(pulses):
                for n in range(max_bright):
                    r.ChangeDutyCycle(n+1)
                    sleep(pwm_delay)
                for n in range(max_bright):
                    r.ChangeDutyCycle(max_bright - (n+1))
                    sleep(pwm_delay)
        sleep(.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    mylcd.lcd_clear()
