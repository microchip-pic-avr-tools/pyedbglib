"""Interface to Spitfire protocol executer, based on Asynchronous Transport interface"""

from logging import getLogger
from ..protocols.ati import AsynchronousTransportInterface
from ..protocols.ati import get_ati_header
from ..protocols.ati import ATI_EXEC_SPITFIRE
from ..protocols.ati import ATI_RESPONSE_BUFFER_SIZE
from ..pyedbglib_errors import PyedbglibNotSupportedError
from ..util import binary

SPITFIRE_ENVELOPE_VERSION = 1
SPITFIRE_ENVELOPE_VARIANT = 0

DATA_SOURCE_UNDEFINED = 0xFF
DATA_DEST_UNDEFINED = 0xFF

class SpitfireControllerCommand(object):
    """
    SpitfireControllerCommand wraps a Spitfire communication exchange with the debugger.

    Fields are populated by the client, and a bytestream is then generated and sent to the debugger for execution.
    """

    SPITFIRE_ENVELOPE_DATA_SOURCE_INDEX = 6
    SPITFIRE_ENVELOPE_DATA_DEST_INDEX = 9

    def __init__(self, content=None):
        # Data source ID
        self.data_source = DATA_SOURCE_UNDEFINED
        # Data destination ID
        self.data_dest = DATA_DEST_UNDEFINED
        # Content (raw command bytes)
        self.content = content


    def set_data_source(self, source_id):
        """
        Sets the data source buffer

        :param source_id: data source buffer ID
        """
        self.data_source = source_id

    def set_data_dest(self, destination_id):
        """
        Sets the data dest buffer

        :param destination_id: data dest buffer ID
        """
        self.data_dest = destination_id

    def generate_bytestream(self):
        """
        Turn the envelope into a byte-stream

        :return: byte-stream
        """
        # Start empty
        stream = bytearray()
        # Some envelope meta data
        stream.extend(bytearray([SPITFIRE_ENVELOPE_VERSION, SPITFIRE_ENVELOPE_VARIANT]))
        # Content itself
        stream.extend(self.content)
        # Source ID
        stream[self.SPITFIRE_ENVELOPE_DATA_SOURCE_INDEX] = self.data_source
        # Dest ID
        stream[self.SPITFIRE_ENVELOPE_DATA_DEST_INDEX] = self.data_dest
        return stream

class SpitfireController(AsynchronousTransportInterface):
    """Wrapper for Spitfire commands in 5G FW."""

    def __init__(self, transport):
        AsynchronousTransportInterface.__init__(self, transport)
        self.logger = getLogger(__name__)

    def new_command(self, content=None):
        """
        Create a new controller command

        :param content: Raw content to add to the new command
        :type content: bytes
        """
        return SpitfireControllerCommand(content)

    def start_spitfire_execution(self, command):
        """
        Starts a Spitfire command execution and returns immediately

        :param command: Raw command bytes
        :type command: bytearray
        """
        cmd = get_ati_header(ATI_EXEC_SPITFIRE)
        # Note only single command, no command or primitive blocks
        cmd.extend(command)
        self.write_command_buffer(cmd)

    def receive_spitfire_execution_response(self):
        """
        Read response from Spitfire command execution

        :returns: Status byte as 4 byte array
        :rtype: bytes
        """
        response = bytearray([0x00]*4)
        # From a spitfire command there will only be a single byte response, but for compatibility with the primitive
        # executer a 4-byte response array is returned
        response[0] = self.read_response_buffer(ATI_RESPONSE_BUFFER_SIZE)[0]
        return response

    def execute(self, command):
        """
        Execute Spitfire command

        :param command: Raw command bytes of command to execute
        :type command: bytes
        :returns: result
        :rtype: bytes
        """
        self.start_spitfire_execution(command)
        return self.receive_spitfire_execution_response()

    def execute_single_block(self, command):
        """
        Execute Spitfire command

        This is the same as the execute() function, kept for API compatibility

        :param command: Raw command bytes of command to execute
        :type command: bytes
        :returns: result
        :rtype: bytes
        """
        return self.execute(command)
