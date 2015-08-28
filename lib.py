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
    if digits == 2:
        return '0' + str(value) if len(str(value)) < 2 else str(value)
    if digits == 3:
        return '00' + str(value) if len(str(value)) == 1 else ('0' + str(value) if len(str(value)) == 2 else str(value))



