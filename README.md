# Yardstick Technical Challenge

This repository contains the Python driver and the hardware design files meant for a take-home assignment offered by [Yardstick](https://www.useyardstick.com/). 

## Task Briefing

Your task is to create a thermostat that will also log temperature with a 10sec period. We've already chosen to integrate this into the Raspberry Pi CM4 system we are using, and to use the AD7414 temperature sensor chip. You are expected to create the electrical interface from the AD7414 to the Raspberry Pi and write the little bit of software to drive it.

The schematic has been started, and is provided for you as a kicad file, but really this is an exercise so feel completely free to return your answer as pen drawn on the PDF if that's easier. The pins GPIO0-GPIO13 are available to you, but I2C bus 0 has some devices on it already so do not use it so as to avoid contention for the bus. To the schematic, add 2 Watts of switchable heat, using a heating element of your choice. Make sure to specify it properly, either a part number if you're using something off the shelf, or construction details if making one from scratch. The heating element can be either board-mounted or attached by wires.


Write enough Python software to use this as a thermostat that can keep the temperature above a set point as well as log the temperature averaged over the last ten seconds, every ten seconds. Target Python 3.6 and write against the following API for board support.

## My Submission
 I used an ADT7420 temperature sensor. This was because AD7414 were generally not available from major distributors and I approached this problem as if I were actually designing a PCB for a real-life project. This repository includes the python drivers. 
 
 * `adt7420.py` - Drivers for the ADT7420 Temperature Sensor
 * `thermostat.py` - Thermostat class for interfacing temperature sensor and turn on heater

## Hardware

The Eagle PCB schematic and layout files are available in the `hardware` folder. It also includes a BOM file and Gerber files.

## Sources
1. My STM32 drivers for ADT7410 - [Link](https://github.com/sai-ydev/adt7410)
2. Analog ADT74x0 driver - [Link](https://github.com/analogdevicesinc/EVAL-ADICUP360/tree/master/projects/ADuCM360_demo_adt7420_pmdz)
