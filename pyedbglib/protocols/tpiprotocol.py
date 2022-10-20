"""
Simple wrapper for TPI programming protocol over JTAGICE3 transport.

TPI protocol is based on the STK600 / Xmega protocol XPROG.

Important note:
    The TPI protocol here is a stub for future implementation.

"""

from logging import getLogger
from .jtagice3protocol import Jtagice3Protocol
from ..util import binary


class TpiProtocolError(Exception):
    """Exception type for TPI command-response wrapping"""
    pass


class TpiProtocol(Jtagice3Protocol):
    """
    Protocol wrapper
    """

    # Protocol commands - these commands are passed into the tool at USB level
    XPRG_CMD_ENTER_PROGMODE = 0x01
    XPRG_CMD_LEAVE_PROGMODE = 0x02
    XPRG_CMD_ERASE = 0x03
    XPRG_CMD_WRITE_MEM = 0x04
    XPRG_CMD_READ_MEM = 0x05
    XPRG_CMD_CRC = 0x06
    XPRG_CMD_SET_PARAM = 0x07

    # Responses
    XPRG_ERR_OK = 0x00
    XPRG_ERR_FAILED = 0x01
    XPRG_ERR_COLLISION = 0x02
    XPRG_ERR_TIMEOUT = 0x03
    XPRG_ERR_ILLEGAL_PARAM = 0x04
    XPRG_ERR_UNKNOWN_COMMAND = 0x10

    # Memory types
    XPRG_MEM_TYPE_APPL = 0x01
    XPRG_MEM_TYPE_BOOT = 0x02
    XPRG_MEM_TYPE_EEPROM = 0x03
    XPRG_MEM_TYPE_FUSE = 0x04
    XPRG_MEM_TYPE_LOCKBITS = 0x05
    XPRG_MEM_TYPE_USERSIG = 0x06
    XPRG_MEM_TYPE_FACTORY_CALIBRATION = 0x07

    # Erase modes
    XPRG_ERASE_CHIP = 0x01
    XPRG_ERASE_APP = 0x02
    XPRG_ERASE_BOOT = 0x03
    XPRG_ERASE_EEPROM = 0x04
    XPRG_ERASE_APP_PAGE = 0x05
    XPRG_ERASE_BOOT_PAGE = 0x06
    XPRG_ERASE_EEPROM_PAGE = 0x07
    XPRG_ERASE_USERSIG = 0x08
    XPRG_ERASE_CONFIG = 0x09

    # XPROG parameters
    XPRG_PARAM_NVMBASE = 0x01
    XPRG_PARAM_EEPPAGESIZE = 0x02
    XPRG_PARAM_NVMCMD_ADDR = 0x03
    XPRG_PARAM_NVMCSR_ADDR = 0x04
    XPRG_PARAM_FLPAGESIZE = 0x05
    XPRG_PARAM_WORDS_PER_WRITE = 0x10

    def __init__(self, transport):
        self.logger = getLogger(__name__)
        Jtagice3Protocol.__init__(self, transport, Jtagice3Protocol.HANDLER_TPI)

    def _tpi_cmd_resp(self, cmd):
        """Send a command, receive a response, and check its validity & status"""
        resp = self.jtagice3_command_response(cmd)
        if not resp[0] == cmd[0]:
            raise TpiProtocolError("TPI protocol: Invalid response received")
        if not resp[1] == TpiProtocol.XPRG_ERR_OK:
            raise TpiProtocolError("TPI protocol: Command failed")
        return resp[2:]

    def enter_progmode(self):
        """Enter programming mode"""
        command = bytearray([TpiProtocol.XPRG_CMD_ENTER_PROGMODE])
        self._tpi_cmd_resp(command)

    def leave_progmode(self):
        """Leave programming mode"""
        command = bytearray([TpiProtocol.XPRG_CMD_LEAVE_PROGMODE])
        self._tpi_cmd_resp(command)

    def read_memory(self, memory_type, address, numbytes):
        """
        Read memory from the AVR over TPI

        :param memory_type: memory type identifier to read
        :param address: address on TPI system to read from
        :numbytes: number of bytes to read
        """
        command = bytearray([TpiProtocol.XPRG_CMD_READ_MEM, memory_type])
        command += bytearray(binary.pack_be32(address))
        command += bytearray(binary.pack_be16(numbytes))
        resp = self._tpi_cmd_resp(command)
        return resp
