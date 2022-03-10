
import smbus
from time import sleep

# ADT7420 registers addresses
TEMP_MSB_REG = 0x00
TEMP_LSB_REG = 0x01
STATUS_REG = 0x02
CONFIG_REG  = 0x03
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
TEMP_HYSTERSIS_SETPOINT = 5

DEFAULT_CONFIG = (
    FAULT_TRIGGER_4 | CT_PIN_POLARITY | INT_PIN_POLARITY |
    INT_CT_MODE |CONTINUOUS_CONVERSION_MODE | RESOLUTION_13_BITS
)


class ADT7420:

    def __init__(self, addr, config=DEFAULT_CONFIG):
        self._addr = addr
        self._bus = smbus.SMBus(1)
        self._config = config
        self.reset()
        self.write_byte(CONFIG_REG, self._config)
        high_set_point = self.convert_temp_to_hex(TEMP_HIGH_SETPOINT)
        msb = high_set_point >> 8
        lsb = high_set_point & 0x00FF
        self.write_word(T_HIGH_SETPOINT_MSB_REG, [msb, lsb])


    def read_byte(self, reg_addr):
        reg_data = None
        try:
            reg_data = self._bus.read_byte_data(self._addr, reg_addr)
        except Exception as error:
            print(error)

        return reg_data

    def read_word(self, reg_addr):
        results = None
        try:
            results = self._bus.read_i2c_block_data(self._addr, reg_addr, 2)
        except Exception as error:
            print(error)
        return results

    def write_byte(self, reg_addr, data):
        try:
            self._bus.write_byte_data(self._addr, reg_addr, data)
        except Exception as error:
            print(error)

    def write_word(self, reg_addr, data):
        try:
            self._bus.write_block_data(self._addr,reg_addr, data)
        except Exception as error:
            print(error)

    # convert temp to hex value
    def convert_temp_to_hex(self, temp):
        hex_value = 0

        # 16 bit or 13 bit
        if self._config & 0x80 == 0x80:
            if temp < 0:
                hex_value = (temp * 128) + 65536
            else:
                hex_value = temp * 128
        else:
            if temp < 0:
                hex_value = (temp * 16) + 8192
                hex_value = hex_value << 3
            else:
                hex_value = temp * 16
                hex_value = hex_value << 3

        return hex_value

    # convert hex to temp value
    def convert_hex_to_temp(self, hex):
        temp_value = 0.0

        # 16 bit or 13 bit
        if hex & 0x8000 == 0x8000:
            if self._config & 0x80 == 0x80:
                temp_value = (hex - 65536) / 128
            else:
                hex = hex >> 3
                temp_value = (hex - 8192) / 16
        else:
            if self._config & 0x80 == 0x80:
                temp_value = hex / 128
            else:
                hex = hex >> 3
                temp_value = hex / 16

        return temp_value


    def read_id(self):
        return self.read_byte(ID_REG)

    def read_temp(self):
        results = self.read_word(TEMP_MSB_REG)
        raw_value = (results[0] << 8) + results[1]
        return self.convert_hex_to_temp(raw_value)

    def reset(self):
        # reset command
        try:
            self._bus.write_byte(self._addr, SOFTWARE_RESET)
        except:
            print("Failed to reset")

        # reset takes a few microseconds
        sleep(1)


if __name__ == "__main__":
    adc = ADT7420(0x48)
    if adc.read_id() == 0xCB:
        print("Chip read successful")
    else:
        print("No ADC detected")
        exit(1)
    while True:
        temp_C = adc.read_temp()
        print("Temperature: {0} C".format(temp_C))
        sleep(2)
