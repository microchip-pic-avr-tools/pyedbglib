"""
CMSIS-DAP wrapper for custom commands (using vendor extensions)
This mechanism is used to pass JTAGICE3-style commands for AVR devices
over the CMSIS-DAP interface
"""
import time
from logging import getLogger
from ..util.binary import unpack_be16
from ..util import print_helpers
from .cmsisdap import CmsisDapUnit


class AvrCommandError(Exception):
    """
    Exception type for AVR command-response wrapping
    """
    pass


class AvrCommand(CmsisDapUnit):
    """
    Wraps AVR command and responses
    """

    # Vendor Commands used to transport AVR over CMSIS-DAP
    AVR_COMMAND = 0x80
    AVR_RESPONSE = 0x81
    AVR_EVENT = 0x82
    AVR_MORE_FRAGMENTS = 0x00
    AVR_FINAL_FRAGMENT = 0x01

    # Payload limits.  Usually 512, but may be lower.
    AVR_COMMAND_RESPONSE_MAX_PAYLOAD = 512

    # Packet structure - command (sending a command)
    AVR_CMD_COMMAND_HEADER_CMD = 0
    AVR_CMD_COMMAND_HEADER_FRAGMENT_NUMBER = 1
    AVR_CMD_COMMAND_HEADER_SIZE = 2
    AVR_CMD_COMMAND_HEADER_PAYLOAD_START = 4

    # Packet structure - command response (reply to command send)
    AVR_CMD_RESPONSE_HEADER_CMD = 0
    AVR_CMD_RESPONSE_FRAGMENT_CODE = 1

    # Packet structure - response (polling for a response)
    AVR_RSP_COMMAND_HEADER_RSP = 0

    # Packet structure - response (reply to response poll)
    AVR_RSP_RESPONSE_HEADER_RSP = 0
    AVR_RSP_RESPONSE_HEADER_FRAGMENT_NUMBER = 1
    AVR_RSP_RESPONSE_HEADER_SIZE = 2
    AVR_RSP_RESPONSE_HEADER_PAYLOAD_START = 4

    # Packet structure - event (polling for an event)
    AVR_EVENT_COMMAND_HEADER_EVT = 0

    # Packet structure - event (reply to event polling)
    AVR_EVENT_RESPONSE_HEADER_EVT = 0
    AVR_EVENT_RESPONSE_HEADER_SIZE = 1
    AVR_EVENT_RESPONSE_HEADER_PAYLOAD_START = 3

    # Events are in practise between 8 and 14 bytes.  In theory:
    AVR_EVENT_RESPONSE_MIN_SIZE = 6
    AVR_EVENT_RESPONSE_MAX_SIZE = 64-AVR_EVENT_RESPONSE_HEADER_PAYLOAD_START

    # Retry delay on AVR receive frame
    AVR_RETRY_DELAY_MS = 50

    def __init__(self, transport, no_timeouts=False):
        self.no_timeouts = no_timeouts
        self.timeout = 1000
        CmsisDapUnit.__init__(self, transport)
        self.ep_size = transport.get_report_size()
        self.payload_start = self.ep_size - self.AVR_CMD_COMMAND_HEADER_PAYLOAD_START
        self.logger = getLogger(__name__)
        self.logger.debug("Created AVR command on DAP wrapper")

    def poll_events(self):
        """
        Polling for events from AVRs

        :returns: bytearray containing a received event, or None
        """
        self.logger.debug("Polling AVR events")
        resp = self.dap_command_response(bytearray([self.AVR_EVENT]))
        if resp:
            if resp[self.AVR_EVENT_RESPONSE_HEADER_EVT] == self.AVR_EVENT:
                # Unpack number of event bytes
                event_data_size = unpack_be16(resp[1:3])
                event_payload_start = self.AVR_EVENT_RESPONSE_HEADER_PAYLOAD_START
                self.logger.debug("AVR event of size %d received", event_data_size)
                # Sanity check for size before returning the payload
                if self.AVR_EVENT_RESPONSE_MIN_SIZE <= event_data_size < self.AVR_EVENT_RESPONSE_MAX_SIZE:
                    return resp[event_payload_start:event_payload_start+event_data_size]
        return None

    def _avr_response_receive_frame(self):
        retries = int(self.timeout / self.AVR_RETRY_DELAY_MS)
        # Get the delay in seconds
        delay = self.AVR_RETRY_DELAY_MS / 1000
        while retries or self.no_timeouts:
            resp = self.dap_command_response(bytearray([self.AVR_RESPONSE]))
            if resp[self.AVR_RSP_RESPONSE_HEADER_RSP] != self.AVR_RESPONSE:
                # Response received is not valid.  Abort.
                raise AvrCommandError("AVR response DAP command failed; invalid token: 0x{:02X}"
                                      .format(resp[self.AVR_RSP_RESPONSE_HEADER_RSP]))
            if resp[self.AVR_RSP_RESPONSE_HEADER_FRAGMENT_NUMBER] != self.AVR_MORE_FRAGMENTS:
                return resp
            self.logger.debug("Resp: %s", print_helpers.bytelist_to_hex_string(resp))

            # Delay in seconds
            time.sleep(delay)
            retries -= 1
        raise AvrCommandError("AVR response timeout")

    # Chops command up into fragments
    def _fragment_command_packet(self, command_packet):
        packets_total = int((len(command_packet) / (self.payload_start)) + 1)
        self.logger.debug("Fragmenting AVR command into {:d} chunks".format(packets_total))
        fragments = []
        for i in range(0, packets_total):
            command_fragment = bytearray([self.AVR_COMMAND, ((i + 1) << 4) + packets_total])
            if (len(command_packet) - (i * (self.payload_start))) > (self.payload_start):
                length = self.payload_start
            else:
                length = len(command_packet) - (i * (self.payload_start))

            command_fragment.append(int(length >> 8))
            command_fragment.append(int(length & 0xFF))

            for j in range(0, self.payload_start):
                if j < length:
                    command_fragment.append(command_packet[i * (self.payload_start) + j])
                else:
                    command_fragment.append(0x00)

            fragments.append(command_fragment)
        return fragments

    # Sends an AVR command and waits for response
    def avr_command_response(self, command):
        """
        Sends an AVR command and receives a response

        :param command: Command bytes to send
        :return: Response bytes received
        """
        fragments = self._fragment_command_packet(command)
        self.logger.debug("Sending AVR command")
        for fragment in fragments:
            self.logger.debug("Sending AVR command 0x{:02X}".format(fragment[self.AVR_CMD_COMMAND_HEADER_CMD]))
            resp = self.dap_command_response(fragment)
            if resp[self.AVR_CMD_RESPONSE_HEADER_CMD] != self.AVR_COMMAND:
                raise AvrCommandError("AVR command DAP command failed; invalid token: 0x{:02X}"
                                      " - is another session active?"
                                      .format(resp[self.AVR_CMD_RESPONSE_HEADER_CMD]))
            if fragment == fragments[-1]:
                if resp[self.AVR_CMD_RESPONSE_FRAGMENT_CODE] != self.AVR_FINAL_FRAGMENT:
                    raise AvrCommandError("AVR command DAP command failed; invalid final fragment ack: 0x{:02X}"
                                          .format(resp[self.AVR_CMD_RESPONSE_FRAGMENT_CODE]))
            else:
                if resp[self.AVR_CMD_RESPONSE_FRAGMENT_CODE] != self.AVR_MORE_FRAGMENTS:
                    raise AvrCommandError("AVR command DAP command failed; invalid non-final fragment ack: 0x{:02X}"
                                          .format(resp[self.AVR_CMD_RESPONSE_FRAGMENT_CODE]))

        # Receive response
        fragment_info, _, response = self._avr_response_receive_fragment()
        packets_remaining = (fragment_info & 0xF) - 1
        for _ in range(0, packets_remaining):
            fragment_info, _, data = self._avr_response_receive_fragment()
            response.extend(data)
        return response

    def _avr_response_receive_fragment(self):
        fragment = []
        # Receive a frame
        response = self._avr_response_receive_frame()

        # Get the payload size from the header information
        size = unpack_be16(response[self.AVR_RSP_RESPONSE_HEADER_SIZE:self.AVR_RSP_RESPONSE_HEADER_SIZE+2])

        # The message header ends at AVR_RSP_RESPONSE_HEADER_PAYLOAD_START
        if len(response) < (self.AVR_RSP_RESPONSE_HEADER_PAYLOAD_START + size):
            raise AvrCommandError("Response size does not match the header information.")

        # Extract data
        for i in range(0, size):
            fragment.append(response[self.AVR_RSP_RESPONSE_HEADER_PAYLOAD_START + i])

        fragment_info = response[self.AVR_RSP_RESPONSE_HEADER_FRAGMENT_NUMBER]
        return fragment_info, size, fragment
