"""
Serial Port Mapper
Kits like Curiosity Nano consist of a composite USB device with multiple interfaces, including
a virtual serial port.  The USB serial number belongs on a device level.  This utility offers a
mechanism for linking the virtual serial port to its parent USB device.
"""
from __future__ import print_function
import os
from logging import getLogger
from ..hidtransport.hidtransportfactory import hid_transport

if os.name == "nt":
    from .wincdc import CDC
else:
    import serial.tools.list_ports


class SerialPortMap(object):
    """
    This is a utility to find virtual serial port name based on HID device serial number,
    or vice versa.
    """
    def __init__(self):
        """
        Create map of tools and ports based on serial number matching. Method used is
        very different on Windows and other platforms.
        """
        # Hook onto logger
        self.logger = getLogger(__name__)

        self.portmap = []
        tools = hid_transport().devices
        if os.name == "nt":
            # On Windows, use registry lookup impemented in wincdc.py
            cdc = CDC()
            for tool in tools:
                if tool.serial_number:
                    name = tool.product_string.split(" ")[0].lower()
                    # Snap and PICkit4 are identified by their second-names:
                    if name == 'mplab':
                        name = tool.product_string.split(" ")[1].lower()
                    port = cdc.find_cdc_port(name, tool.serial_number)
                    if port:
                        self.portmap.append({"tool": tool, "port": port})
        else:
            # On Mac & Linux, all info needed is found using serial.ports.list_ports.
            usbports = [p for p in serial.tools.list_ports.comports() if "USB" in p.hwid]
            for tool in tools:
                for port in usbports:
                    if tool.serial_number and tool.serial_number == port.serial_number:
                        self.portmap.append({"tool": tool, "port": port.device})


    def find_matching_tools_ports(self, serial_endswith):
        """
        Find tools and ports matching (partial) serial number.

        :param serial_endswith: serial number, or at least end part thereof
        :return: List of matching {tool, port} dicts
        """
        matches = []
        for item in self.portmap:
            if item["tool"].serial_number.endswith(serial_endswith):
                matches.append(item)
        return matches


    def find_serial_port(self, serial_number):
        """
        Find virtual serial port based on serial number exact match

        :param serial_number: serial number of tool
        :return: Name of virtual serial port or None.
        """
        for item in self.portmap:
            if item["tool"].serial_number == serial_number:
                return item["port"]
        return None


    def find_hid_tool(self, port):
        """
        Find HID tool based on virtual serial port name

        :param port: port name to find
        :return: HID tool object or None
        """
        for item in self.portmap:
            if item["port"] == port:
                return item["tool"]
        return None


    def find_serial_number(self, port):
        """
        Find HID tool serial number based on virtual serial port name
        This is redundant, but added for convenience

        :param port: port name
        :return: HID tool serial number or None
        """
        tool = self.find_hid_tool(port)
        return tool.serial_number if tool else None
