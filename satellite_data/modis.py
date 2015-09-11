#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from osgeo import gdal
from datetime import datetime

from QC4SD.satellite_data.satellite_data import SatelliteData
from QC4SD.lib import fix_zeros
from QC4SD.quality_control.modis import ModisQC


class MODIS(SatelliteData):

    def __init__(self, file):
        """Initialize the class of MODIS products

        :param file: path to input file
        :type file: str
        """
        super().list.append(self)
        super().__init__(file)

        # load metadata
        self.satellite = self.metadata['ASSOCIATEDPLATFORMSHORTNAME']  # Terra
        self.shortname = self.metadata['SHORTNAME']  # MOD09A1
        self.tile = self.metadata['LOCALGRANULEID'].split('.')[2]  # h10v07
        self.longname = self.metadata['LONGNAME']  # MODIS/Terra Surface Reflectance 8-Day L3 Global 500m SIN Grid
        dt_d = [int(x) for x in self.metadata['PRODUCTIONDATETIME'].split('T')[0].split('-')]
        dt_h = [int(x) for x in self.metadata['PRODUCTIONDATETIME'].replace('.', ':').split('T')[1].split(':')[0:3]]
        self.datetime = datetime(dt_d[0], dt_d[1], dt_d[2], dt_h[0], dt_h[1], dt_h[2])
        self.date_str = "{0}-{1}-{2}".format(self.datetime.year,
                                             fix_zeros(self.datetime.month, 2),
                                             fix_zeros(self.datetime.day, 2))

        # save in globals vars of class
        SatelliteData.satellite = self.satellite
        SatelliteData.shortname = self.shortname
        SatelliteData.tile = self.tile

        self.set_quality_control_bands()

    def set_quality_control_bands(self):
        """Create all quality control bands class (ModisQC)
        based on the type of MODIS products. Create one
        Modis quality control (ModisQC) for each quality
        control band of this satellite data instance.
        """

        self.qc_bands = {}

        # for MOD09/MYD09 A1
        if self.shortname in ['MOD09A1', 'MYD09A1']:
            # define numbers of bits for the band value in binary

            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if '_qc_' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name, num_bits=32)
            # Solar Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'szen' in x[1]][0][0]
            self.qc_bands['sza'] = ModisQC(self.shortname, 'sza', qc_name)
            # View Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'vzen' in x[1]][0][0]
            self.qc_bands['vza'] = ModisQC(self.shortname, 'vza', qc_name)
            # Relative Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'raz' in x[1]][0][0]
            self.qc_bands['rza'] = ModisQC(self.shortname, 'rza', qc_name)
            # State flags
            qc_name = [x for x in self.sub_datasets if '_state_' in x[1]][0][0]
            self.qc_bands['sf'] = ModisQC(self.shortname, 'sf', qc_name, num_bits=16)

        # for MOD09/MYD09 Q1
        if self.shortname in ['MOD09Q1', 'MYD09Q1']:
            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if '_qc_' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name)

    def get_data_band(self, band):
        """Return the raster of the data band for respective band
        of the file.

        :param band: band to process
        :type band: int
        :return: raster of the data band
        :rtype: ndarray
        """
        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name)
        data_band_raster = gdal_data_band.ReadAsArray()
        del gdal_data_band
        return data_band_raster

    def get_nodata_value(self, band):
        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name)
        return gdal_data_band.GetRasterBand(1).GetNoDataValue()

    def get_quality_control_bands(self, band):
        return [x for x in self.sub_datasets if 'b0'+str(band) in x[1]][0][0]

    def get_total_pixels(self):
        rows = int(self.metadata["DATAROWS500M"])
        columns = int(self.metadata["DATACOLUMNS500M"])
        return rows*columns