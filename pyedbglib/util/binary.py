"""Packing and unpacking numbers into bytearrays of 8-bit values with various endian encodings"""

from numbers import Integral

def _check_input_value(value, bits):
    """
    :param value: An integer
    :param bits: Number of bits used to represent this integer
    :return: Raises an OverflowError if the value is too large
    """
    # Be sure to support both py2 and py3
    if not isinstance(value, Integral):
        raise TypeError("The input {} is not an Integral type".format(value))

    if value > (2 ** bits) - 1:
        raise OverflowError("Value {} is larger than the maximum value {}".format(value, (2 ** bits) - 1))


def pack_le32(value):
    """
    Packs a 32-bit value into a bytearray in little-endian form

    :param value: input value
    :return: 32-bit little endian bytearray representation of the input value
    """
    _check_input_value(value, 32)
    return bytearray([value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF])


def pack_be32(value):
    """
    Packs a 32-bit value into a bytearray in big-endian form

    :param value: input value
    :return: 32-bit big endian bytearray representation of the input value
    """
    _check_input_value(value, 32)
    return bytearray(
        [(value >> 24) & 0xFF,
         (value >> 16) & 0xFF,
         (value >> 8) & 0xFF,
         value & 0xFF])


def pack_le24(value):
    """
    Packs a 24-bit value into a bytearray in little-endian form

    :param value: input value
    :return: 24-bit little endian bytearray representation of the input value
    """
    _check_input_value(value, 24)
    return bytearray([value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF])


def pack_be24(value):
    """
    Packs a 24-bit value into a bytearray in big-endian form

    :param value: input value
    :return: 24-bit big endian bytearray representation of the input value
    """
    _check_input_value(value, 24)
    return bytearray(
        [(value >> 16) & 0xFF,
         (value >> 8) & 0xFF,
         value & 0xFF])


def pack_le16(value):
    """
    Packs a 16-bit value into a bytearray in little-endian form

    :param value: input value
    :return: 16-bit little endian bytearray representation of the input value
    """
    _check_input_value(value, 16)
    return bytearray([value & 0xFF, (value >> 8) & 0xFF])


def pack_be16(value):
    """
    Packs a 16-bit value into a bytearray in big-endian form

    :param value: input value
    :return: 16-bit big endian bytearray representation of the input value
    """
    _check_input_value(value, 16)
    return bytearray([(value >> 8) & 0xFF, value & 0xFF])


def _check_input_array(data, length):
    """
    Used to check if a bytearray or list of 8-bit values has the correct length to convert to an integer

    :param data: bytearray (or list) representing a value
    :param length: Expected length of the list
    :return: Raises a ValueError if len(data) is not the same as length
    """
    if not isinstance(data, (list, bytearray)):
        raise TypeError("The input {} is not a list of bytearray".format(data))

    if len(data) != length:
        raise ValueError("Input data {} does not have length {}".format(data, length))


def unpack_le32(data):
    """
    Unpacks a little-endian 32-bit value from a bytearray

    :param data: 32-bit little endian bytearray representation of an integer
    :return: integer value
    """
    _check_input_array(data, 4)
    return data[0] + (data[1] << 8) + (data[2] << 16) + (data[3] << 24)


def unpack_be32(data):
    """
    Unpacks a big-endian 32-bit value from a bytearray

    :param data: 32-bit big endian bytearray representation of an integer
    :return: integer value
    """
    _check_input_array(data, 4)
    return data[3] + (data[2] << 8) + (data[1] << 16) + (data[0] << 24)


def unpack_le24(data):
    """
    Unpacks a little-endian 32-bit value from a bytearray

    :param data: 24-bit little endian bytearray representation of an integer
    :return: integer value
    """
    _check_input_array(data, 3)
    return data[0] + (data[1] << 8) + (data[2] << 16)


def unpack_be24(data):
    """
    Unpacks a big-endian 24-bit value from a bytearray

    :param data: 24-bit big endian bytearray representation of an integer
    :return: integer value
    """
    _check_input_array(data, 3)
    return data[2] + (data[1] << 8) + (data[0] << 16)


def unpack_le16(data):
    """
    Unpacks a little-endian 16-bit value from a bytearray

    :param data: 16-bit little endian bytearray representation of an integer
    :return: integer value
    """
    _check_input_array(data, 2)
    return data[0] + (data[1] << 8)


def unpack_be16(data):
    """
    Unpacks a big-endian 16-bit value from a bytearray

    :param data: 16-bit big endian bytearray representation of an integer
    :return: integer value
    """
    _check_input_array(data, 2)
    return data[1] + (data[0] << 8)
