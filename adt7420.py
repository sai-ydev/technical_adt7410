#!/usr/bin/env python3

"""ADT7420 Driver

This module provides the requisite drivers for interfacing
the ADT74xx class ADC drivers
"""
import sys
from time import sleep
import smbus


# ADT7420 registers addresses
TEMP_MSB_REG = 0x00
TEMP_LSB_REG = 0x01
STATUS_REG = 0x02
CONFIG_REG = 0x03
T_HIGH_SETPOINT_MSB_REG = 0x04
T_HIGH_SETPOINT_LSB_REG = 0x05
T_LOW_SETPOINT_MSB_REG = 0x06
T_LOW_SETPOINT_LSB_REG = 0x07
T_CRIT_SETPOINT_MSB_REG = 0x08
T_CRIT_SETPOINT_LSB_REG = 0x09
T_HYST_SETPOINT_REG = 0x0A
ID_REG = 0x0B
SOFTWARE_RESET = 0x2F

# ADT7420 I2C Address
ADT7420_ADDRESS = 0x48
ADT7420_ID = 0xCB

HIGH = 0
LOW = 1

# ADT7420 Setup parameters
FAULT_TRIGGER_1 = 0x00
FAULT_TRIGGER_2 = 0x01
FAULT_TRIGGER_3 = 0x02
FAULT_TRIGGER_4 = 0x03

CT_PIN_POLARITY = (LOW << 2)
INT_PIN_POLARITY = (LOW << 3)
INT_CT_MODE = (HIGH << 4)

CONTINUOUS_CONVERSION_MODE = 0x00
ONE_SHOT_MODE = 0x20
ONE_SAMPLE_PER_SECOND_MODE = 0x40
SHUTDOWN_MODE = 0x60

RESOLUTION_13_BITS = 0x00
RESOLUTION_16_BITS = 0x80

# Default Temperature monitoring parameters
TEMP_HIGH_SETPOINT = 75
TEMP_LOW_SETPOINT = 0
TEMP_CRITICAL_SETPOINT = 100
TEMP_HYSTERSIS_SETPOINT = 2

DEFAULT_CONFIG = (
    FAULT_TRIGGER_4 | CT_PIN_POLARITY | INT_PIN_POLARITY |
    INT_CT_MODE | CONTINUOUS_CONVERSION_MODE | RESOLUTION_13_BITS
)


class ADT7420:
    """ Class for ADT family ADCs """

    def __init__(self, bus=1, addr=0x48, config=DEFAULT_CONFIG):
        self._addr = addr
        self._bus = smbus.SMBus(bus)
        self._config = config
        self.reset()
        self.write_byte(CONFIG_REG, self._config)

    def read_byte(self, reg_addr):
        """ Read bytes from register """
        reg_data = None
        try:
            reg_data = self._bus.read_byte_data(self._addr, reg_addr)
        except IOError:
            pass

        return reg_data

    def read_word(self, reg_addr):
        """ Read 2 bytes from register """
        results = None
        try:
            results = self._bus.read_i2c_block_data(self._addr, reg_addr, 2)
        except IOError:
            pass
        return results

    def write_byte(self, reg_addr, data):
        """ Write one byte to register """
        try:
            self._bus.write_byte_data(self._addr, reg_addr, data)
        except IOError:
            pass

    def write_word(self, reg_addr, data):
        """ Write 2 bytes to register """
        try:
            self._bus.write_i2c_block_data(self._addr, reg_addr, data)
        except IOError:
            pass

    # convert temp to hex value
    def convert_temp_to_hex(self, temp_value):
        """ Converts temperature value to hex """
        hex_value = 0

        # 16 bit or 13 bit
        if self._config & 0x80 == 0x80:
            if temp_value < 0:
                hex_value = (temp_value * 128) + 65536
            else:
                hex_value = temp_value * 128
        else:
            if temp_value < 0:
                hex_value = (temp_value * 16) + 8192
                hex_value = hex_value << 3
            else:
                hex_value = temp_value * 16
                hex_value = hex_value << 3

        return hex_value

    # convert hex to temp value
    def convert_hex_to_temp(self, raw_hex):
        """ Converts raw hex to temperature """
        temp_value = 0.0

        # 16 bit or 13 bit
        if raw_hex & 0x8000 == 0x8000:
            if self._config & 0x80 == 0x80:
                temp_value = (raw_hex - 65536) / 128
            else:
                raw_hex = raw_hex >> 3
                temp_value = (raw_hex - 8192) / 16
        else:
            if self._config & 0x80 == 0x80:
                temp_value = raw_hex / 128
            else:
                raw_hex = raw_hex >> 3
                temp_value = raw_hex / 16

        return temp_value

    def set_temp_reg(self, reg, temp_value):
        """ Set temperature register """
        temp_hex = self.convert_temp_to_hex(temp_value)
        msb = temp_hex >> 8
        lsb = temp_hex & 0x00FF
        self.write_word(reg, [msb, lsb])

    def get_temp_reg(self, reg):
        """ Returns temperature register setting """
        result = self.read_word(reg)
        if result:
            raw_value = (result[0] << 8) + result[1]
            return self.convert_hex_to_temp(raw_value)
        return None

    def read_temp(self):
        """ Reads Temperature MSB first """
        results = self.read_word(TEMP_MSB_REG)
        if results:
            raw_value = (results[0] << 8) + results[1]
            return self.convert_hex_to_temp(raw_value)
        return None

    def read_id(self):
        """ Returns Chip ID """
        return self.read_byte(ID_REG)

    def reset(self):
        """ Software reset of the ADC """
        try:
            self._bus.write_byte(self._addr, SOFTWARE_RESET)
        except IOError:
            pass

        # reset takes a few microseconds
        sleep(1)


if __name__ == "__main__":

    temp_sensor = ADT7420(bus=1, addr=0x48)

    if temp_sensor.read_id() == 0xCB:
        print("Chip read successful")
    else:
        print("No ADC detected")
        sys.exit(1)

    while True:
        temp = temp_sensor.read_temp()
        if temp:
            print("Temperature: {0} C".format(temp))
        sleep(2)
