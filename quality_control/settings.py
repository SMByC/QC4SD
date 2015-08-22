#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import os
import configparser


class QualityControlConfig:

    def __init__(self, config_file):
        self.config_file = config_file

    def load(self):
        config = configparser.RawConfigParser()
        config.read(self.config_file)

    def check(self):
        pass