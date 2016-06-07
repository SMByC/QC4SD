#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015-2016
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

try:
    from osgeo import gdal
except ImportError:
    import gdal

from qc4sd.quality_control.modis import mxd09a1, mxd09q1


class ModisQC:
    """Quality control class for MODIS files. One instance represent
    one band of quality control for specific type of MODIS products.
    Each type of MODIS products has different bands of quality control
    and rules for check the quality control for one pixel.
    """

    def __init__(self, sd_shortname, id_name, qc_name, num_bits=None):
        self.sd_shortname = sd_shortname
        self.id_name = id_name
        self.qc_name = qc_name
        self.num_bits = num_bits
        # get raster for quality control band
        gdal_dataset_qc = gdal.Open(self.qc_name, gdal.GA_ReadOnly)
        self.quality_control_raster = gdal_dataset_qc.ReadAsArray()
        del gdal_dataset_qc
        # statistics for invalid pixel in respective field
        self.invalid_pixels = {}
        # this quality band need to be check
        self.need_check = True

        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1 (Collection 6)
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:

            # set the full name for this quality control band
            if self.id_name == 'rbq': self.full_name = 'Reflectance Band Quality'
            if self.id_name == 'sza': self.full_name = 'Solar Zenith Angle'
            if self.id_name == 'vza': self.full_name = 'View Zenith Angle'
            if self.id_name == 'rza': self.full_name = 'Relative Zenith Angle'
            if self.id_name == 'sf':  self.full_name = 'Reflectance State QA flags'

        # [MXD09Q1] ########################################################
        # for MOD09Q1 and MYD09Q1 (Collection 6)
        if self.sd_shortname in ['MOD09Q1', 'MYD09Q1']:

            # set the full name for this quality control band
            if self.id_name == 'sf':  self.full_name = 'Reflectance State QA flags'
            if self.id_name == 'rbq': self.full_name = 'Reflectance Band Quality'

    def init_statistics(self, qcf):
        """Configure and initialize statistics values. This need to be
        called for restart statistics for process quality control check
        for each new satellite data.

        :param qcf: quality control file
        :type qcf: configparse
        """
        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:

            # create and init the statistics fields dictionary to zero count value,
            # for specific quality control band (id_name) that belonging this instance
            keys_from_qcf = list(qcf['MXD09A1'].keys())
            self.invalid_pixels = dict((k, 0) for k in keys_from_qcf if k.startswith(self.id_name+'_'))

            # verification if this quality band type need to check:
            # if all items of this qc type in qcf are True, this means
            # that this qc don't need to be check, all pass this qc
            single_qcf_values = set([v for k,v in qcf['MXD09A1'].items() if k.startswith(self.id_name+'_')])
            if len(single_qcf_values) == 1 and single_qcf_values.pop() == 'true':
                self.need_check = False
            if self.id_name == 'sza' or self.id_name == 'vza':
                if qcf.getint('MXD09A1', self.id_name+'_min') == 0 and qcf.getint('MXD09A1', self.id_name+'_max') == 180:
                    self.need_check = False
            if self.id_name == 'rza':
                if qcf.getint('MXD09A1', self.id_name+'_min') == -180 and qcf.getint('MXD09A1', self.id_name+'_max') == 180:
                    self.need_check = False

        # [MXD09Q1] ########################################################
        # for MOD09Q1 and MYD09Q1
        if self.sd_shortname in ['MOD09Q1', 'MYD09Q1']:

            # create and init the statistics fields dictionary to zero count value,
            # for specific quality control band (id_name) that belonging this instance
            keys_from_qcf = list(qcf['MXD09Q1'].keys())
            self.invalid_pixels = dict((k, 0) for k in keys_from_qcf if k.startswith(self.id_name+'_'))

            # verification if this quality band type need to check:
            # if all items of this qc type in qcf are True, this means
            # that this qc don't need to be check, all pass this qc
            single_qcf_values = set([v for k,v in qcf['MXD09Q1'].items() if k.startswith(self.id_name+'_')])
            if len(single_qcf_values) == 1 and single_qcf_values.pop() == 'true':
                self.need_check = False

    def quality_control_check(self, x, y, band, qcf):
        """Check if the specific pixel in x and y position pass or not
        pass all quality controls, this is evaluate with the quality
        control value for the respective pixel position. The quality
        controls is evaluate based on the quality control file.

        :param x: raster position in x for the pixel
        :type x: int
        :param y: raster position in y for the pixel
        :type y: int
        :param band: band of data to process
        :type band: int
        :param qcf: quality control file
        :type qcf:
        :return: check list
        :rtype: dict
        """
        # pass the qc if this quality band don't need to be check
        if self.need_check is False:
            return True

        # get the pixel value for specific band of quality control
        qc_pixel_value = self.quality_control_raster.item((x, y))

        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1 (Collection 6)
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:
            # switch case for quality control band
            quality_control_band = {
                'rbq': mxd09a1.rbq,
                'sza': mxd09a1.sza,
                'vza': mxd09a1.vza,
                'rza': mxd09a1.rza,
                'sf': mxd09a1.sf,
            }
            return quality_control_band[self.id_name](self, qcf, band, qc_pixel_value)

        # [MXD09Q1] ########################################################
        # for MOD09Q1 and MYD09Q1 (Collection 6)
        if self.sd_shortname in ['MOD09Q1', 'MYD09Q1']:
            # switch case for quality control band
            quality_control_band = {
                'sf': mxd09q1.sf,
                'rbq': mxd09q1.rbq,
            }
            return quality_control_band[self.id_name](self, qcf, band, qc_pixel_value)