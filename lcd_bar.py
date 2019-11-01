import I2C_LCD_driver
import time
import random
import math

fontdata1 = [
        # char(0) - Left Bracket
        [ 0b00111,
          0b00100,
          0b00100,
          0b00100,
          0b00100,
          0b00100,
          0b00111 ],

        # char(1) - 1 unit
        [ 0b10000,
          0b10000,
          0b10000,
          0b10000,
          0b10000,
          0b10000,
          0b10000 ],

        # char(2) - 2 units
        [ 0b11000,
          0b11000,
          0b11000,
          0b11000,
          0b11000,
          0b11000,
          0b11000,
          0b11000 ],

        # char(3) - 3 units
        [ 0b11100,
          0b11100,
          0b11100,
          0b11100,
          0b11100,
          0b11100,
          0b11100,
          0b11100 ],

        # char(4) - 4 units
        [ 0b11110,
          0b11110,
          0b11110,
          0b11110,
          0b11110,
          0b11110,
          0b11110,
          0b11110 ],

        # char(5) - 5 units
        [ 0b11111,
          0b11111,
          0b11111,
          0b11111,
          0b11111,
          0b11111,
          0b11111,
          0b11111 ],

        # char(6) - Empty Char
        [ 0b00000,
          0b00000,
          0b00000,
          0b00000,
          0b00000,
          0b00000,
          0b00000,
          0b00000 ],

        # char(7) - Right Bracket
        [ 0b11100,
          0b00100,
          0b00100,
          0b00100,
          0b00100,
          0b00100,
          0b00100,
          0b11100 ],
]

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_load_custom_chars(fontdata1)

row_pos = {"1st": 0x00, "2nd": 0x40, "3rd": 0x14, "4th": 0x54}

value_range = (0.017, 0.027)

try:
    while True:
        mylcd.lcd_clear()

        random_value = random.uniform(value_range[0], value_range[1])
        print(random_value)
        bar_value = round(90*(random_value / value_range[1]))
        print(bar_value)

        char_nums = [0, 0, 0, 0, 0, 0]

        if bar_value % 5 != 0:
            char_nums[(bar_value % 5) - 1] = 1
        char_nums[4] = math.trunc(bar_value / 5)

        char_nums.reverse()
        char_nums[5] = 18 - sum(char_nums)
        print(char_nums)

        mylcd.lcd_write(0x80 + row_pos.get("3rd"))

        mylcd.lcd_write_char(0) # Left Bracket
        idx = 0
        for val in char_num:
            for n in range(val):
                mylcd.lcd_write_char(5-idx)
            idx += 1
        mylcd.lcd_write_char(7) # Right Bracket

        time.sleep(2)
except KeyboardInterrupt:
    exit()
