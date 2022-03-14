#!/usr/bin/env python3
""" Thermostat class

This module implements a thermostat that reads temperature from a sensor
and controls a heater.

"""
import logging
import time
import sys
import signal
import RPi.GPIO as GPIO
import adt7420

INT_PIN = 13
HEATER = 5

HIGH = 1
LOW = 0

class Thermostat:
    """ Thermostat class """
    def __init__(self, bus=1, address=0x48, temperature=0, hysteresis=5):
        # ADC is configured to be 13 bits by default
        self._adc = adt7420.ADT7420(bus, address)

        if self._adc.read_id() == adt7420.ADT7420_ID:
            logging.log(logging.INFO, "ADT7414 initialized successfully!")
        else:
            raise Exception("Missing ADC Chip")

        self._under_temp = temperature
        self._hysteresis = hysteresis
        self._heater = False

        #moving window of temperature
        self._temp_data = list()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(INT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(HEATER, GPIO.OUT)

        GPIO.add_event_detect(
            INT_PIN, GPIO.FALLING,
            callback=self.int_callback, bouncetime=100
        )
        GPIO.output(HEATER, LOW)

    def measure_temperature(self):
        """ returns temperature from the sensor """
        return self._adc.read_temp()

    def _log_temperature(self, temperature):
        """ Call this when you want to record the temperature in the logs. When used
        in production there will be a logging profile to make it just route to
        the appropriate place. """
        logging.log(logging.INFO, f'{time.asctime()}: AD7414 {temperature} degC')

    def one_hz(self):
        """This will get called once per second by the main software, from a thread
        set aside to do this (that is to say, don't worry about spawning your own
        thread here). You can assume that you don't need to protect against the
        supervisory software crashing and failing to run this call."""
        temperature = self.measure_temperature()
        avg = 0.0
        if temperature:
            self._temp_data.append(temperature)

        if len(self._temp_data) >= 10:
            avg = sum(self._temp_data) / len(self._temp_data)
            self._log_temperature(avg)
            del self._temp_data[:10]

            # Turn off heater?
            if avg > (self._under_temp + self._hysteresis) and self._heater:
                GPIO.output(HEATER, LOW)
                self._heater = False

    def set_temperature(self, temperature):
        """ Set the under temperature parameter """
        self._under_temp = temperature
        self._adc.set_temp_reg(adt7420.T_LOW_SETPOINT_MSB_REG, temperature)

    def set_hysteresis(self, value):
        """Setting the hysteresis parameter """
        self._hysteresis = value
        self._adc.set_temp_reg(adt7420.T_HYST_SETPOINT_REG, value)

    def int_callback(self, pin):
        """ Interrupt callback for turning on heater """
        if not GPIO.input(pin):
            self._heater = True
            GPIO.output(HEATER, HIGH)


def signal_handler():
    """ Cleanup of GPIO pins upone exit"""
    GPIO.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    thermostat = Thermostat()

    thermostat.set_temperature(25)
    thermostat.set_hysteresis(2)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        thermostat.one_hz()
        time.sleep(1)
