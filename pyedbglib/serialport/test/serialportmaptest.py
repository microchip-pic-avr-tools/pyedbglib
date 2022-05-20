
"""
Manual test for SerialPortMap
"""
from __future__ import print_function
import sys
from pyedbglib.serialport.serialportmap import SerialPortMap


if __name__ == '__main__':
    """
    Print port map, test methods if arguments given
    """
    portmap = SerialPortMap()
    sn = sys.argv[1] if len(sys.argv) > 1 else ""
    for item in portmap.find_matching_tools_ports(sn):
        print("{} S/N {} port {}".format(
            item["tool"].product_string, item["tool"].serial_number, item["port"]))

    if len(sys.argv) > 2:
        print("\n")
    for arg in sys.argv[2:]:
        print("find_serial_port({})  = {}".format(arg, portmap.find_serial_port(arg)))
        print("find_serial_number({}) = {}".format(arg, portmap.find_serial_number(arg)))
