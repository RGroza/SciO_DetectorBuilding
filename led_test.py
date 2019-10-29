import RPi.GPIO as GPIO
from time import sleep
from random import random

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

redLED = 8
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

max_bright = 80 # max brightness of PWM cycle
pwm_delay = .05 # delay between cycles

degree_sign= u'\N{DEGREE SIGN}'

try:
    while True:
        randTemp = round(75*random(), 1)
        if randTemp < 25:
            print(str(randTemp) + degree_sign + "C: low temp")
            for n in range(5):
                for n in range(max_bright):
                    b.ChangeDutyCycle(n)
                    sleep(pwm_delay)
                for n in range(max_bright):
                    b.ChangeDutyCycle(max_bright - n)
                    sleep(pwm_delay)
            # for n in range(5):
            #     GPIO.output(blueLED, GPIO.HIGH)
            #     sleep(.5)
            #     GPIO.output(blueLED, GPIO.LOW)
            #     sleep(.5)
        elif randTemp < 50:
            print(str(randTemp) + degree_sign + "C: medium temp")
            for n in range(5):
                for n in range(max_bright):
                    g.ChangeDutyCycle(n)
                    sleep(pwm_delay)
                for n in range(max_bright):
                    g.ChangeDutyCycle(max_bright - n)
                    sleep(pwm_delay)
            # for n in range(5):
            #     GPIO.output(greenLED, GPIO.HIGH)
            #     sleep(.5)
            #     GPIO.output(greenLED, GPIO.LOW)
            #     sleep(.5)
        else:
            print(str(randTemp) + degree_sign + "C: high temp")
            for n in range(5):
                for n in range(max_bright):
                    r.ChangeDutyCycle(n)
                    sleep(pwm_delay)
                for n in range(max_bright):
                    r.ChangeDutyCycle(max_bright - n)
                    sleep(pwm_delay)
            # for n in range(5):
            #     GPIO.output(redLED, GPIO.HIGH)
            #     sleep(.5)
            #     GPIO.output(redLED, GPIO.LOW)
            #     sleep(.5)
        sleep(2)

except KeyboardInterrupt:
    GPIO.cleanup()
