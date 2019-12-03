from time import sleep
import smbus
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# ads1x15
# CircuitPython base class driver for ADS1015/1115 ADCs.
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice

_ADS1X15_DEFAULT_ADDRESS = const(0x48)
_ADS1X15_POINTER_CONVERSION = const(0x00)
_ADS1X15_POINTER_CONFIG = const(0x01)
_ADS1X15_CONFIG_OS_SINGLE = const(0x8000)
_ADS1X15_CONFIG_MUX_OFFSET = const(12)
_ADS1X15_CONFIG_COMP_QUE_DISABLE = const(0x0003)
_ADS1X15_CONFIG_GAIN = {
    2/3: 0x0000,
    1:   0x0200,
    2:   0x0400,
    4:   0x0600,
    8:   0x0800,
    16:  0x0A00
}

class Mode:
    """An enum-like class representing possible ADC operating modes."""
    # See datasheet "Operating Modes" section
    # values here are masks for setting MODE bit in Config Register
    CONTINUOUS = 0x0000
    SINGLE = 0x0100

class ADS1x15(object):
    """Base functionality for ADS1x15 analog to digital converters."""

    def __init__(self, i2c, gain=1, data_rate=None, mode=Mode.SINGLE,
                 address=_ADS1X15_DEFAULT_ADDRESS):
        self._last_pin_read = None
        self.buf = bytearray(3)
        self._data_rate = self._gain = self._mode = None
        self.gain = gain
        self.data_rate = self._data_rate_default() if data_rate is None else data_rate
        self.mode = mode
        self.i2c_device = I2CDevice(i2c, address)

    @property
    def data_rate(self):
        """The data rate for ADC conversion in samples per second."""
        return self._data_rate

    @data_rate.setter
    def data_rate(self, rate):
        possible_rates = self.rates
        if rate not in possible_rates:
            raise ValueError(
                "Data rate must be one of: {}".format(possible_rates))
        self._data_rate = rate

    @property
    def rates(self):
        """Possible data rate settings."""
        raise NotImplementedError('Subclass must implement rates property.')

    @property
    def rate_config(self):
        """Rate configuration masks."""
        raise NotImplementedError(
            'Subclass must implement rate_config property.')

    @property
    def gain(self):
        """The ADC gain."""
        return self._gain

    @gain.setter
    def gain(self, gain):
        possible_gains = self.gains
        if gain not in possible_gains:
            raise ValueError("Gain must be one of: {}".format(possible_gains))
        self._gain = gain

    @property
    def gains(self):
        """Possible gain settings."""
        g = list(_ADS1X15_CONFIG_GAIN.keys())
        g.sort()
        return g

    @property
    def mode(self):
        """The ADC conversion mode."""
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode != Mode.CONTINUOUS and mode != Mode.SINGLE:
            raise ValueError("Unsupported mode.")
        self._mode = mode

    def read(self, pin, is_differential=False):
        """I2C Interface for ADS1x15-based ADCs reads.
        params:
            :param pin: individual or differential pin.
            :param bool is_differential: single-ended or differential read.
        """
        pin = pin if is_differential else pin + 0x04
        return self._read(pin)

    def _data_rate_default(self):
        """Retrieve the default data rate for this ADC (in samples per second).
        Should be implemented by subclasses.
        """
        raise NotImplementedError(
            'Subclasses must implement _data_rate_default!')

    def _conversion_value(self, raw_adc):
        """Subclasses should override this function that takes the 16 raw ADC
        values of a conversion result and returns a signed integer value.
        """
        raise NotImplementedError(
            'Subclass must implement _conversion_value function!')

    def _read(self, pin):
        """Perform an ADC read. Returns the signed integer result of the read."""
        if self.mode == Mode.CONTINUOUS and self._last_pin_read == pin:
            return self._conversion_value(self.get_last_result(True))
        else:
            self._last_pin_read = pin
            config = _ADS1X15_CONFIG_OS_SINGLE
            config |= (pin & 0x07) << _ADS1X15_CONFIG_MUX_OFFSET
            config |= _ADS1X15_CONFIG_GAIN[self.gain]
            config |= self.mode
            config |= self.rate_config[self.data_rate]
            config |= _ADS1X15_CONFIG_COMP_QUE_DISABLE
            self._write_register(_ADS1X15_POINTER_CONFIG, config)

            if self.mode == Mode.SINGLE:
                while not self._conversion_complete():
                    pass

            return self._conversion_value(self.get_last_result(False))

    def _conversion_complete(self):
        """Return status of ADC conversion."""
        # OS is bit 15
        # OS = 0: Device is currently performing a conversion
        # OS = 1: Device is not currently performing a conversion
        return self._read_register(_ADS1X15_POINTER_CONFIG) & 0x8000

    def get_last_result(self, fast=False):
        """Read the last conversion result when in continuous conversion mode.
        Will return a signed integer value. If fast is True, the register
        pointer is not updated as part of the read. This reduces I2C traffic
        and increases possible read rate.
        """
        return self._read_register(_ADS1X15_POINTER_CONVERSION, fast)

    def _write_register(self, reg, value):
        """Write 16 bit value to register."""
        self.buf[0] = reg
        self.buf[1] = (value >> 8) & 0xFF
        self.buf[2] = value & 0xFF
        with self.i2c_device as i2c:
            i2c.write(self.buf)

    def _read_register(self, reg, fast=False):
        """Read 16 bit register value. If fast is True, the pointer register
        is not updated.
        """
        with self.i2c_device as i2c:
            if fast:
                i2c.readinto(self.buf, end=2)
            else:
                i2c.write_then_readinto(bytearray([reg]), self.buf, in_end=2)
        return self.buf[0] << 8 | self.buf[1]

# ads1115
# CircuitPython driver for 1115 ADCs.
import struct
#pylint: disable=unused-import
from .ads1x15 import ADS1x15, Mode

# Data sample rates
_ADS1115_CONFIG_DR = {
    8:    0x0000,
    16:   0x0020,
    32:   0x0040,
    64:   0x0060,
    128:  0x0080,
    250:  0x00A0,
    475:  0x00C0,
    860:  0x00E0
}

# Pins
P0 = 0
P1 = 1
P2 = 2
P3 = 3

class ADS1115(ADS1x15):
    """Class for the ADS1115 16 bit ADC."""

    @property
    def bits(self):
        """The ADC bit resolution."""
        return 16

    @property
    def rates(self):
        """Possible data rate settings."""
        r = list(_ADS1115_CONFIG_DR.keys())
        r.sort()
        return r

    @property
    def rate_config(self):
        """Rate configuration masks."""
        return _ADS1115_CONFIG_DR

    def _data_rate_default(self):
        return 128

    def _conversion_value(self, raw_adc):
        raw_adc = raw_adc.to_bytes(2, "big")
        value = struct.unpack(">h", raw_adc)[0]
        return value


# analog_in
# AnalogIn for single-ended and differential ADC readings.
_ADS1X15_DIFF_CHANNELS = {
    (0, 1): 0,
    (0, 3): 1,
    (1, 3): 2,
    (2, 3): 3
}
_ADS1X15_PGA_RANGE = {
    2/3: 6.144,
    1:   4.096,
    2:   2.048,
    4:   1.024,
    8:   0.512,
    16:  0.256
}
# pylint: enable=bad-whitespace

class AnalogIn():
    """AnalogIn Mock Implementation for ADC Reads."""

    def __init__(self, ads, positive_pin, negative_pin=None):
        """AnalogIn
        :param ads: The ads object.
        :param ~digitalio.DigitalInOut positive_pin: Required pin for single-ended.
        :param ~digitalio.DigitalInOut negative_pin: Optional pin for differential reads.
        """
        self._ads = ads
        self._pin_setting = positive_pin
        self._negative_pin = negative_pin
        self.is_differential = False
        if negative_pin is not None:
            pins = (self._pin_setting, self._negative_pin)
            if pins not in _ADS1X15_DIFF_CHANNELS:
                raise ValueError("Differential channels must be one of: {}"
                                 .format(list(_ADS1X15_DIFF_CHANNELS.keys())))
            self._pin_setting = _ADS1X15_DIFF_CHANNELS[pins]
            self.is_differential = True

    @property
    def value(self):
        """Returns the value of an ADC pin as an integer."""
        return self._ads.read(self._pin_setting,
                              is_differential=self.is_differential) << (16 - self._ads.bits)

    @property
    def voltage(self):
        """Returns the voltage from the ADC pin as a floating point value."""
        volts = self.value * _ADS1X15_PGA_RANGE[self._ads.gain] / 32767
        return volts

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
