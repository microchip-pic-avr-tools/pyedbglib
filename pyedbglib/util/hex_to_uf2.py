'''
    Converts Intel hex files to UF2-format.

    This is a stripped-down and modified version of
    the "uf2conv.py" from https://github.com/microsoft/uf2/tree/master/utils
        Note that the magic numbers are changed to match the firmware ones,
        and do not hold the default values from Github.

    The script is modified to
        - support blocks with payload of less than 256 bytes
        - not enforce each UF2 block to start on 256 byte boundaries
        - support gaps in the hex file content
'''
import struct
import re
from logging import getLogger

# The magic numbers here must correspond to the ones in the firmware
UF2_CNANO_START0 = 0x0A324655 # "UF2\n"
UF2_CNANO_START1 = 0x1E1130F6
UF2_CNANO_END    = 0x0A8AA692

MAX_UF2_BLOCK_PAYLOAD = 256

def is_hex(buf):
    """Check if buffer contains Intel hex content

    :param buf: Buffer containing text, typically read from file
    :type buf: bytes
    :return: True if content is valid Intel hex format, False if not
    :rtype: bool
    """
    try:
        w = buf[0:30].decode("utf-8")
    except UnicodeDecodeError:
        return False
    if w[0] == ':' and re.match(b"^[:0-9a-fA-F\r\n]+$", buf):
        return True
    return False

class Block:
    """UF2 block
    """
    def __init__(self, addr):
        """
        :param addr: Start address for the block (byte address)
        :type addr: int
        """
        self.addr = addr
        self.payload = bytearray()

    def encode(self, blockno, numblocks):
        """Makes a block containing up to MAX_UF2_BLOCK_PAYLOAD databytes

        :param blockno: Block number
        :type blockno: int
        :param numblocks: Total number of blocks
        :type numblocks: int
        :return: Packed bytes object
        :rtype: bytes
        """
        familyid = 0x0  # Not implemented and should therefore be 0
        flags = 0x0     # Not implemented and should therefore be 0

        payloadsize = len(self.payload)
        if payloadsize > MAX_UF2_BLOCK_PAYLOAD:
            raise ValueError("Too big payload, {}, max is {}".format(payloadsize, MAX_UF2_BLOCK_PAYLOAD))
        hd = struct.pack("<IIIIIIII",
            UF2_CNANO_START0, UF2_CNANO_START1,
            flags, self.addr, len(self.payload), blockno, numblocks, familyid)
        hd += self.payload
        while len(hd) < 512 - 4:
            hd += b"\x00"
        hd += struct.pack("<I", UF2_CNANO_END)
        return hd

def convert_from_hex_to_uf2(buf):
    """Convert buffer with Intel hex content to UF2 format

    :param buf: Buffer containing Intel hex content
    :type buf: bytes
    :return: Data converted to UF2 format
    :rtype: bytes
    """
    logger = getLogger(__name__)
    # The application start-address should be None, as the hexfile contains the correct address-offset
    appstartaddr = None
    # The current address in the hex. This must be kept between loop iterations to detect gaps in the hex content
    addr = 0
    upper = 0
    currblock = None
    blocks = []
    # Convert Intelhex-lines into blocks
    for line in buf.split('\n'):
        if line[0] != ":":
            continue
        i = 1
        rec = []
        while i < len(line) - 1:
            rec.append(int(line[i:i+2], 16))
            i += 2
        tp = rec[3] # Record type
        if tp == 4: # Extended Linear Address
            upper = ((rec[4] << 8) | rec[5]) << 16
        elif tp == 2: # Extended Segment Address
            upper = ((rec[4] << 8) | rec[5]) << 4
        elif tp == 1: # End Of File
            break
        elif tp == 0: # Data
            nextaddr = upper + ((rec[1] << 8) | rec[2])
            if appstartaddr is None:
                appstartaddr = nextaddr
            # If there is a gap in the hex file a new block must be started.
            # Simply padding the gap does not help as the padding will be interpreted as actual data values and will
            # be written to the target memory. Instead a new block must be started no matter how small the gap is to
            # make sure the UF2 parser on the receiver side detects the gap
            if nextaddr != addr:
                currblock = Block(nextaddr)
                blocks.append(currblock)
            addr = nextaddr
            i = 4
            while i < len(rec) - 1:
                # Create a new block if no blocks has been started or the current block is full
                if not currblock or len(currblock.payload)>=MAX_UF2_BLOCK_PAYLOAD:
                    currblock = Block(addr)
                    blocks.append(currblock)
                currblock.payload.append(rec[i])
                addr += 1
                i += 1
    numblocks = len(blocks)
    # Add the blocks to the result file
    resfile = b""
    for i in range(0, numblocks):
        resfile += blocks[i].encode(i, numblocks)

    logger.info("Converted hex to UF2, output size: %d, start address: 0x%x, number of blocks: %d",
                  len(resfile),
                  appstartaddr,
                  numblocks)
    return resfile

def hex_to_uf2(hex_filename, uf2_filename):
    """Convert Intel hex file to UF2 file

    :param hex_filename: Path to hex file to convert
    :type hex_filename: path-like object
    :param uf2_filename: Path to UF2 file to be generated. If the file already exists it will be overwritten
    :type uf2_filename: path-like object
    :raises ValueError: If the provided hex file is not valid
    """
    logger = getLogger(__name__)
    logger.info("Start UF2 conversion")

    # read input-file
    with open(hex_filename, mode='rb') as f:
        inbuf = f.read()

    # Check if it is a hex-file, and if so convert it to a uf2-file
    if is_hex(inbuf):
        logger.info("Valid hex-file confirmed")
        outbuf = convert_from_hex_to_uf2(inbuf.decode("utf-8"))
        # Write the result to the UF2 file
        with open(uf2_filename, "wb") as uf2file:
            uf2file.write(outbuf)
        logger.info("Wrote %d bytes to %s", len(outbuf), uf2_filename)

    else:
        raise ValueError("{} is not a hex-file, could not convert".format(hex_filename))
