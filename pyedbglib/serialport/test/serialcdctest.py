"""
Manual test for SerialCDC
"""
from __future__ import print_function
import sys
import logging
from time import sleep
from serial.serialutil import SerialException
from pyedbglib.serialport.serialcdc import SerialCDC


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: {} port [timeout]".format(sys.argv[0]), file=sys.stderr)
        sys.exit(2)

    baud = 9600
    port = sys.argv[1]
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    try:
        if len(sys.argv) > 2:
            com = SerialCDC(port, baud, timeout=5, open_timeout=int(sys.argv[2]))
        else:
            com = SerialCDC(port, baud, timeout=5)
        print("read/write test port {} baud {}".format(port, baud))
        com.write(b'\r')
        print(com.read_until(b'\004'))
        com.close()
            
    except SerialException as e:
        print(e)

