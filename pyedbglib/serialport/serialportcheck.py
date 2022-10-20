"""
Utility for checking whether a (virtual) serial port is accessible or not.
"""

import sys
import os
from logging import getLogger
if sys.platform.startswith("linux"):
    import grp


def check_access(port):
    """
    Check if user has access to kit's virtual serial port.
    In many Linux distros access requires membership of the 'dialout' group which is not default.

    :param port: port name to check
    :return: boolean - access is allowed
    """
    logger = getLogger(__name__)
    if port and not sys.platform.startswith("win32"):
        try:
            # Open for read - "w" would try to create file if non-existent
            with open(port, "r") as _:
                pass
        except IOError as e:
            logger.error(e)
            if isinstance(e, PermissionError) and sys.platform.startswith("linux"):
                logger.error("Unable to open port '%s'", port)
                # If there is a group named "dialout" and user is not member, print advice.
                try:
                    dialout = grp.getgrnam("dialout")
                    if not dialout.gr_gid in os.getgroups():
                        logger.error("To access '%s' the user must be a member of the 'dialout' group", port)
                        logger.error("To fix: console command 'sudo adduser $USER dialout' then log out and in again")
                except KeyError:
                    # If there is no dialout group, then there is nothing that can be done
                    pass
                logger.error("Be sure that read/write access is granted with: 'sudo chmod a+rw %s'", port)
            return False
    return True
