#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import configparser


def quality_control_config(config_file):

    config = configparser.RawConfigParser()
    config.read(config_file)

    return config
