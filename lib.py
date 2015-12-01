#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Some functions and libraries
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co


###############################################################################

def fix_zeros(value, digits):
    """Adjust the left zeros for integer numbers.

    For example:
    value:    3,   23
    digits:   3,    3
    return: 003,  023

    :param value: integer value to adjust
    :type value: int
    :param digits: number of digits to adjust (2 or 3)
    :type digits: int
    :return: number adjusted
    :rtype: str
    """
    assert isinstance(value, int), "value must be a integer"
    assert digits in [2, 3], "digits must be 2 or 3"
    if digits == 2:
        return '0' + str(value) if len(str(value)) < 2 else str(value)
    if digits == 3:
        return '00' + str(value) if len(str(value)) == 1 else ('0' + str(value) if len(str(value)) == 2 else str(value))


def fix_binary_string(bin_str, num_bits):
    """Fix the binary string with the number of bits, if the number of bits
    in the binary string is less than the num_bits, this adding zeros in the
    left string in the binary number.

    For example:
    bin_str="1011"
    num_bits=6
    return="001011"

    :param bin_str: binary string
    :type bin_str: str
    :param num_bits: number of bits
    :type num_bits: int
    :return: binary string adjusted
    :rtype: str
    """
    assert num_bits >= len(bin_str), "num_bits is greater than the length of bin_str"
    return '0'*(num_bits-len(bin_str))+bin_str


def int2bin(value):
    """Convert integer value to binary

    :param value: integer value
    :type value: int
    :return: binary number
    :rtype: str
    """
    assert isinstance(value, int), "value must be a integer"
    return "{0:b}".format(value)


def chunks(l, n):
    """Split a list into evenly sized chunks

    :param l: list to chunk
    :type l: list
    :param n: n sizes to chunk
    :type n: int
    :rtype: list
    """
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]
