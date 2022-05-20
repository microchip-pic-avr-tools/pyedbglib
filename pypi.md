# pyedbglib - Python EDBG protocol library
pyedbglib is a low-level protocol library for communicating with Microchip CMSIS-DAP based debuggers

![PyPI - Format](https://img.shields.io/pypi/format/pyedbglib)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyedbglib)
![PyPI - License](https://img.shields.io/pypi/l/pyedbglib)

## Overview
pyedbglib is available:

* install using pip from pypi: https://pypi.org/project/pyedbglib
* browse source code on github: https://github.com/microchip-pic-avr-tools/pyedbglib
* read API documentation on github: https://microchip-pic-avr-tools.github.io/pyedbglib
* read the changelog on github: https://github.com/microchip-pic-avr-tools/pyedbglib/blob/main/CHANGELOG.md

## Usage
pyedbglib is a library which can be used by Python applications to communicate with Microchip microcontrollers via Microchip CMSIS-DAP based debuggers.

The protocol is documented in the [EDBG communication protocol](https://onlinedocs.microchip.com/pr/GUID-33422CDF-8B41-417C-9C31-E4521ADAE9B4-en-US-2/index.html).

## Supported debuggers
pyedbglib supports:
* PKOB nano (nEDBG) - on-board debugger on Curiosity Nano
* MPLAB PICkit 4 In-Circuit Debugger (when in 'AVR mode')
* MPLAB Snap In-Circuit Debugger (when in 'AVR mode')
* Atmel-ICE
* Power Debugger
* EDBG - on-board debugger on Xplained Pro/Ultra
* mEDBG - on-board debugger on Xplained Mini/Nano
* JTAGICE3 (firmware version 3.0 or newer)

Note: Each debugger may implement a subset of protocols and commands.

## Example
```python
"""
Example usage of pyedbglib to read debugger firmware version and target voltage
"""
from pyedbglib.hidtransport.hidtransportfactory import hid_transport
from pyedbglib.protocols.housekeepingprotocol import Jtagice3HousekeepingProtocol
from pyedbglib.version import VERSION as pyedbglib_version

# Report library version
print("pyedbglib version {}".format(pyedbglib_version))

# Make a connection using HID transport
transport = hid_transport()
transport.connect()

# Create a housekeeper
housekeeper = Jtagice3HousekeepingProtocol(transport)
housekeeper.start_session()

# Read out debugger firmware version
major = housekeeper.get_byte(Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONTEXT_CONFIG,
                             Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONFIG_FWREV_MAJ)
minor = housekeeper.get_byte(Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONTEXT_CONFIG,
                             Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONFIG_FWREV_MIN)
build = housekeeper.get_le16(Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONTEXT_CONFIG,
                             Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONFIG_BUILD)
print ("Debugger firmware is version {}.{}.{}".format(major, minor,build))

# Read out target voltage
target_voltage = housekeeper.get_le16(Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONTEXT_ANALOG,
                                      Jtagice3HousekeepingProtocol.HOUSEKEEPING_ANALOG_VTREF)
print ("Target voltage is {:.02f}V".format(target_voltage/1000.0))

# Tear down
housekeeper.end_session()
transport.disconnect()
```

## Notes for Linux® systems
HIDAPI needs to build using packages: libusb-1.0.0-dev, libudev-dev

USB devices need udev rules to be added to a file in /etc/udev/rules.d

Example of udev rules for supported debuggers:
```bash
# HIDAPI/libusb:

# JTAGICE3
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2140", MODE="0666"
# Atmel-ICE
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2141", MODE="0666"
# Power Debugger
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2144", MODE="0666"
# EDBG - debugger on Xplained Pro
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2111", MODE="0666"
# EDBG - debugger on Xplained Pro (MSD mode)
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2169", MODE="0666"
# mEDBG - debugger on Xplained Mini
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2145", MODE="0666"
# PKOB nano (nEDBG) - debugger on Curiosity Nano
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2175", MODE="0666"
# PKOB nano (nEDBG) in DFU mode - bootloader of debugger on Curiosity Nano
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2fc0", MODE="0666"
# MPLAB PICkit 4 In-Circuit Debugger
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2177", MODE="0666"
# MPLAB Snap In-Circuit Debugger
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="2180", MODE="0666"
```

pyedbglib also provides helper functions for accessing serial ports.  The user has to be part of the 'dialout' group to allow this.  This can be done by executing:
```bash
sudo adduser $USER dialout
```

It may also be necessary to grant read+write permission to the port, for example:
```bash
sudo chmod a+rw /dev/ttyACM0
```
