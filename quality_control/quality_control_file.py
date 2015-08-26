#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import configparser


def setup_quality_control_file(qcf):

    quality_control_file = configparser.RawConfigParser()
    quality_control_file.read(qcf)

    print(quality_control_file)
    print(quality_control_file.sections())

    return quality_control_file
