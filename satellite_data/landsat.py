#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

# for future implementation

from QC4SD.satellite_data.satellite_data import SatelliteData


class LandsatFile(SatelliteData):

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def load(self):
        pass
