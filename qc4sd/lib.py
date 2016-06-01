#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Some functions and libraries
#
#  (c) Copyright SMBYC - IDEAM 2015-2016
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from collections import Counter

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


def merge_dicts(a, b):
    """Merge and sums all items with the same keys for two
    dictionaries 'a' and 'b' with support for merge and sums
    items for dicts into the dicts, like this:

        >>> a = {'a': 1, 'b': 2, 'c': 3, 'k': {'t': 5}}
        >>> b = {'b': 3, 'c': 4, 'f': 5, 'k': {'r': 9, 't': 2}}
        >>> merge_dicts(a, b)
        {'a': 1, 'b': 5, 'c': 7, 'f': 5, 'k': {'r': 9, 't': 7}})

    :param a: first dict to merge
    :type a: dict
    :param b: second dict to merge
    :type b: dict
    :return: sums and merge of all items in a container
    :rtype: Counter
    """
    for k, v in a.items():
        if isinstance(v, dict): a[k] = Counter(v)
    for k, v in b.items():
        if isinstance(v, dict): b[k] = Counter(v)
    common_items = []
    for common_key in (set(a) & set(b)):
        if isinstance(a[common_key], Counter) and isinstance(b[common_key], Counter):
            common_items.append((common_key, merge_dicts(a[common_key], b[common_key])))
        else:
            common_items += list((Counter({common_key: a[common_key]}) + Counter({common_key: b[common_key]})).items())
    a_no_common = [(k, a[k]) for k in list(a.keys() - (set(a) & set(b)))]
    b_no_common = [(k, b[k]) for k in list(b.keys() - (set(a) & set(b)))]
    return Counter(dict(a_no_common + b_no_common + common_items))


def frange(start, stop, step):
    """Same as range but with floating steps support

    :rtype: list
    """
    L = []
    while 1:
        next = start + len(L) * step
        if step > 0 and next >= stop:
            break
        elif step < 0 and next <= stop:
            break
        L.append(next)
    return L


def repulsive_items_list(l, repulsive_distance=None, min_distance=None):
    """Separate the items in list if this have less of repulsive distance
    value and separate its elements with the minimum distance.

    :Example:

        >>> l=[1,2,4,10,23,25]
        >>> repulsive_items_list(l, 3, 3)
        [-0.5, 2.5, 5.5, 10, 22.5, 25.5]

    :param l: list to process
    :type l: list
    :param repulsive_distance: minimum value for check the distance between items
    :type repulsive_distance: float
    :param min_distance: minimum distance for separate the items
    :type min_distance: float
    :rtype: list
    """

    if repulsive_distance is None:
        repulsive_distance = max(l)*0.04
    else:
        repulsive_distance -= repulsive_distance*0.01
    if min_distance is None:
        min_distance = repulsive_distance

    ###### group list
    l_sort = sorted(list(zip(range(len(l)), l)), key=lambda x: x[1])
    d = dict(l_sort)

    items_to_fix = []
    for idx, (k, v) in enumerate(l_sort[0:-1]):
        if abs(v - l_sort[idx+1][1]) < repulsive_distance:
            items_to_fix.append([k, l_sort[idx+1][0]])
    if not items_to_fix:
        return False, repulsive_distance, l

    join_groups = []
    group_joined = False
    for group0, group1 in zip(items_to_fix[0:-1], items_to_fix[1::]):
        if group0[-1] == group1[0]:
            if group_joined:
                to_remove = join_groups[-1]
                join_groups.append(join_groups[-1] + group1[1::])
                join_groups.remove(to_remove)
            else:
                join_groups.append(group0 + group1[1::])
            group_joined = True
            if group0 in join_groups:
                join_groups.remove(group0)
        else:
            if group_joined:
                join_groups.append(group1)
            elif group0 in join_groups:
                join_groups.append(group1)
            else:
                join_groups.append(group0)
                if group1 == items_to_fix[-1]:
                    join_groups.append(group1)
            group_joined = False
    if len(items_to_fix) == 1 and not join_groups:
        join_groups = items_to_fix

    ###### fixes list
    def fix_group_distance(group):
        min_value = d[group[0]]
        max_value = d[group[-1]]
        center_value = min_value + (max_value-min_value)/2.0
        if len(group) % 2 == 0:  # even
            side = len(group)*min_distance/2.0 - min_distance/2.0
        else:  # odd
            side = (len(group)-1)*min_distance/2.0
        re_adjust = frange(center_value-side, center_value+side+1, min_distance)
        for item in group:
            pass
        return re_adjust

    for group in join_groups:
        group_fixes = fix_group_distance(group)
        for idx, item in enumerate(group):
            d[item] = group_fixes[idx]

    result = [round(x[1], 3) for x in sorted(d.items(), key=lambda x: x[0])]
    if result == l:
        return False, repulsive_distance, result
    else:
        return True, repulsive_distance, result

