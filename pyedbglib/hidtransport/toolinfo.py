"""Gathering of all known Microchip CMSIS-DAP debuggers and default EP sizes"""

import os
from logging import getLogger
from ..util import binary

# EDBG-based tools use the Atmel Vendor ID
USB_VID_ATMEL = 0x03EB

# List of known useful HID/CMSIS-DAP tools
# 3G tools:
USB_TOOL_DEVICE_PRODUCT_ID_JTAGICE3 = 0x2140
USB_TOOL_DEVICE_PRODUCT_ID_ATMELICE = 0x2141
USB_TOOL_DEVICE_PRODUCT_ID_POWERDEBUGGER = 0x2144
USB_TOOL_DEVICE_PRODUCT_ID_EDBG_A = 0x2111
USB_TOOL_DEVICE_PRODUCT_ID_MSD = 0x2169
USB_TOOL_DEVICE_PRODUCT_ID_ZERO = 0x2157
USB_TOOL_DEVICE_PRODUCT_ID_PUBLIC_EDBG_C = 0x216A
USB_TOOL_DEVICE_PRODUCT_ID_KRAKEN = 0x2170

# 4G tools:
USB_TOOL_DEVICE_PRODUCT_ID_MEDBG = 0x2145

# 5G tools:
USB_TOOL_DEVICE_PRODUCT_ID_NEDBG_HID_MSD_DGI_CDC = 0x2175
USB_TOOL_DEVICE_PRODUCT_ID_PICKIT4_HID_CDC = 0x2177
USB_TOOL_DEVICE_PRODUCT_ID_SNAP_HID_CDC = 0x2180
USB_TOOL_DEVICE_PRODUCT_ID_ICD4_HID_CDC = 0x217C
USB_TOOL_DEVICE_PRODUCT_ID_ICE4_HID_CDC = 0x2193


# The Product String Names are used to identify the tool based on the USB
# device product strings (i.e. these names are usually just a subset of the
# actual product strings)
TOOL_SHORTNAME_TO_USB_PRODUCT_STRING = {
    'atmelice': "Atmel-ICE",
    'powerdebugger': "Power Debugger",
    'pickit4': "MPLAB PICkit 4",
    'snap': "MPLAB Snap",
    'nedbg': "nEDBG",
    'jtagice3': "JTAGICE3",
    'medbg': "mEDBG",
    'edbg': "EDBG",
    'icd4': "MPLAB ICD 4",
    'ice4': "MPLAB ICE 4"
}


"""
Some Atmel/Microchip '3G' tools (EDBG, Atmel-ICE, PowerDebugger) have 'dual configuration' HID interfaces.
The 'default' configuration has a 512-byte HID report size, while the 'strict' and 'minimal' configurations both
have 64-byte report size.  The switching mechanism is not implemented in a USB-standard way; it is managed using
atprogram.exe (part of Microchip Studio 7) and the configuration is persistent in the tool.

The configuration currently in use can be determined by:
    atprogram.exe parameters --get-ep-size
and the configuration can be altered by:
    atprogram.exe parameters --set-ep-size [default|strict|minimal]

On Linux and Mac the configuration can be detected using usb.core, see:
    def detect_hid_packet_size(product_id, serial_number):

On Windows the configuration is adjusted after connecting, see:
    def adjust_hid_packet_size(transport, device):
"""

# These tools have non-standard 'dual configuration' HID interfaces
DUAL_CONFIGURATION_3G_TOOLS = [
    USB_TOOL_DEVICE_PRODUCT_ID_ATMELICE,
    USB_TOOL_DEVICE_PRODUCT_ID_POWERDEBUGGER,
    USB_TOOL_DEVICE_PRODUCT_ID_EDBG_A,
    USB_TOOL_DEVICE_PRODUCT_ID_MSD,
    USB_TOOL_DEVICE_PRODUCT_ID_ZERO,
    USB_TOOL_DEVICE_PRODUCT_ID_PUBLIC_EDBG_C
]

def get_default_report_size(pid):
    """
    Retrieve default EP report size based on known PIDs

    :param pid: product ID
    :return: packet size
    """
    logger = getLogger(__name__)
    hid_tools = [
        # 3G
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_JTAGICE3, 'default_report_size': 512},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_ATMELICE, 'default_report_size': 512},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_POWERDEBUGGER, 'default_report_size': 512},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_EDBG_A, 'default_report_size': 512},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_MSD, 'default_report_size': 512},
        # 4G
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_MEDBG, 'default_report_size': 64},
        # 5G
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_NEDBG_HID_MSD_DGI_CDC, 'default_report_size': 64},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_PICKIT4_HID_CDC, 'default_report_size': 64},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_SNAP_HID_CDC, 'default_report_size': 64},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_ICD4_HID_CDC, 'default_report_size': 64},
        {'pid': USB_TOOL_DEVICE_PRODUCT_ID_ICE4_HID_CDC, 'default_report_size': 64}]

    logger.debug("Looking up report size for pid 0x{:04X}".format(pid))
    for tool in hid_tools:
        if tool['pid'] == pid:
            logger.debug("Default report size is {:d}".format(tool['default_report_size']))
            return tool['default_report_size']
    logger.debug("PID not found! Reverting to 64b.")
    return 64

def tool_shortname_to_product_string_name(shortname):
    """
    Mapping for common short names of tools to product string name

    The intention is that this function is always run on the tool name and that the conversion
    only happens if the name is a known shortname. If the shortname is not known of if the name
    provided is already a valid Product string name then the provided shortname parameter will
    just be returned unchanged. So if the name already is a correct Product string name it is
    still safe to run this conversion funtion on it.

    :param shortname: shortname typically used by atbackend (powerdebugger, atmelice etc.)
    :return: String to look for in USB product strings to identify the tool
    """
    logger = getLogger(__name__)

    if shortname is None:
        logger.debug("Tool shortname is None")
        # This is also valid as the user might have provided no tool name, but the conversion function
        # should still be valid
        return shortname

    shortname_lower = shortname.lower()
    if shortname_lower not in TOOL_SHORTNAME_TO_USB_PRODUCT_STRING:
        logger.debug("%s is not a known tool shortname", shortname)
        # ...but it could be a valid Product string name already so no reason to report an error
        return shortname

    return TOOL_SHORTNAME_TO_USB_PRODUCT_STRING[shortname_lower]

def detect_hid_packet_size(product_id, serial_number):
    """
    pyUSB based HID packet size detection

    On Linux and Mac the configuration in use can easily be determined by inspecting the descriptor.

    :param product_id: USB PID to look for
    :param serial_number: USB serial number to match
    :returns: detected report size, or 0 if no match is found
    """
    logger = getLogger(__name__)
    if product_id in DUAL_CONFIGURATION_3G_TOOLS:
        if not os.name == "nt":
            logger.debug("Atmel/Microchip 3G tool: checking for endpoint size configuration")
            # Late-import for non-windows
            import usb
            # Find all affected tools, if connected
            devices = usb.core.find(find_all=True, idVendor=USB_VID_ATMEL, idProduct=product_id)
            for device in devices:
                # If serial_number is provided, it has to match
                if serial_number == device.serial_number:
                    # Look through all interfaces for HID
                    for interface in device.get_active_configuration():
                        if interface.bInterfaceClass == usb.legacy.CLASS_HID:
                            for endpoint in interface:
                                # Return first EP since they are identical
                                logger.debug("Packet size detected: %d bytes", endpoint.wMaxPacketSize)
                                return endpoint.wMaxPacketSize
    # Return 0: 'unable to detect, revert to default'
    return 0

def adjust_hid_packet_size(transport, device):
    """
    Active HIDAPI based HID packet size detection and adjustment

    Detecting report size using the descriptor before connecting is not simple on Windows.  Instead an active detection
    is done after connecting by sending a small packet to ask the tool for its frame size.  This query frame is small
    enough to succeed on both 64- and 512-byte variants, and an adjustment can be made after detection since HIDAPI on
    Windows is tolerant to EP-size mismatches.

    :param transport: HID transport object, already connected
    :param device: device currently connected.  Size is adjusted before returning
    """
    logger = getLogger(__name__)
    if device.product_id in DUAL_CONFIGURATION_3G_TOOLS:
        if os.name == "nt":
            # Late import for Windows
            from ..protocols.cmsisdap import CmsisDapUnit
            logger.debug("Atmel/Microchip 3G tool: actively probing device for endpoint size configuration")
            # Attempt auto-detection of EP size, but revert to default upon failure
            try:
                # EP size is returned from CMSIS-DAP layer
                logger.debug("Querying tool for actual report size")
                # Use the write-read APIs separately to have access to bytes actually sent
                # Display this for debugging and validation purposes, but not used for actual detection
                bytes_sent = transport.hid_write(bytearray([CmsisDapUnit.ID_DAP_Info, CmsisDapUnit.DAP_ID_PACKET_SIZE]))
                logger.debug("Win32 HIDAPI::write sent %d of %d bytes", bytes_sent, device.packet_size)
                rsp = transport.hid_read()
                # The unit responded with information as to its packet size
                ep_size = binary.unpack_le16(rsp[2:4])
                if ep_size in [64, 512]:
                    device.set_packet_size(ep_size)
                    logger.debug("Using detected report size: %d bytes", ep_size)
                else:
                    logger.warning("Invalid report size returned from tool - using default value.")
            # Intentional catch-all to fall back to default
            except Exception:
                logger.warning("Unable to query report size - using default value.")
