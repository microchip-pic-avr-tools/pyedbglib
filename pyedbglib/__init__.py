"""
Python EDBG protocol communication library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pyedbglib is a low-level protocol library for communicating with
Microchip CMSIS-DAP based debuggers.

Overview
~~~~~~~~

pyedbglib is available:
    * install using pip from pypi: https://pypi.org/project/pyedbglib
    * browse source code on github: https://github.com/microchip-pic-avr-tools/pyedbglib
    * read API documentation on github: https://microchip-pic-avr-tools.github.io/pyedbglib
    * read the changelog on github: https://github.com/microchip-pic-avr-tools/pyedbglib/blob/main/CHANGELOG.md

pyedbglib uses hidapi package with a USB-level driver such as libusb.

Library usage
~~~~~~~~~~~~~

The protocol library has no application usage on its own, but provides
USB-protocol-level tool drivers to applications such as pymcuprog.
In general a two-stage stack implementation is required for using pyedbglib:

    1. Create transport HID layer
    2. Create protocol implementation using this transport layer

All protocols implemented in the library generally take the transport layer
as a parameter to their constructors.

To use pyedbglib as a library for applications, the following usage patterns
can be used:

.. code-block:: python

    # Import and instantiate transport object:
    from pyedbglib.hidtransport.hidtransportfactory import hid_transport
    transport = hid_transport()

    # Connect to any PKOB nano (nEDBG) tool.  Serial number and product are optional, but must
    # be provided if more than one matching unit is connected:
    status = transport.connect(serial_number="", product="nedbg")

    # Example of application using housekeeping protocol to read out the target voltage:
    from pyedbglib.protocols.housekeepingprotocol import Jtagice3HousekeepingProtocol
    housekeeper = Jtagice3HousekeepingProtocol(transport)
    housekeeper.start_session()
    voltage = housekeeper.get_le16(Jtagice3HousekeepingProtocol.HOUSEKEEPING_CONTEXT_ANALOG,
                                   Jtagice3HousekeepingProtocol.HOUSEKEEPING_ANALOG_VTREF)
    voltage = voltage / 1000.0
    housekeeper.end_session()
    print ("Target is running at {0:.02f}V".format(voltage))

"""
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
