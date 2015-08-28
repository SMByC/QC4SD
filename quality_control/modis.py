#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from osgeo import gdal



class ModisQC:

    def __init__(self, sd_shortname, id_name, qc_name):
        self.sd_shortname = sd_shortname
        self.id_name = id_name
        self.qc_name = qc_name
        # get raster for quality control band
        gdal_dataset_qc = gdal.Open(self.qc_name)
        self.quality_control_raster = gdal_dataset_qc.ReadAsArray()
        del gdal_dataset_qc

        self.setup()

    def setup(self):
        if self.id_name == 'rbq':
            self.full_name = 'Reflectance Band Quality'
        if self.id_name == 'sza':
            self.full_name = 'Solar Zenith Angle'
        if self.id_name == 'vza':
            self.full_name = 'View Zenith Angle'
        if self.id_name == 'rza':
            self.full_name = 'Relative Zenith Angle'
        if self.id_name == 'sf':
            self.full_name = 'State flags'

    def quality_control_check(self, x, y, qcf):
        qc_value = self.quality_control_raster.item((x, y))
        check_list = {}

        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:
            if self.id_name == 'rbq':
                pass



