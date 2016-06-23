#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015-2016
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import os
import xml.etree.ElementTree as ET
from datetime import date
try:
    from osgeo import gdal
except ImportError:
    import gdal

from qc4sd.lib import fix_zeros
from qc4sd.satellite_data.satellite_data import SatelliteData
from qc4sd.quality_control.modis import ModisQC


class MODIS(SatelliteData):

    def __init__(self, file, xml_file):
        """Initialize the class of MODIS products

        :param xml_file: path to input xml file
        :type xml_file: str
        :param file: path to input file
        :type file: str
        """
        super().list.append(self)
        super().__init__(file)

        # load metadata
        tree = ET.parse(xml_file)
        self.satellite = list(tree.iter('PlatformShortName'))[0].text  # Terra
        self.shortname = list(tree.iter('ShortName'))[0].text  # MOD09A1
        self.tile = list(tree.iter('LocalGranuleID'))[0].text.split('.')[2]  # h10v07
        # get the beginning date
        dt_d = [int(x) for x in list(tree.iter('RangeBeginningDate'))[0].text.split('-')]
        self.start_date = date(dt_d[0], dt_d[1], dt_d[2])
        # calculate Julian date of the beginning date
        self.start_jday = self.start_date.timetuple().tm_yday
        # year and jday (ie 2015034), equal to filename string
        self.start_year_and_jday = "{0}{1}".format(self.start_date.year, fix_zeros(self.start_jday, 3))

        # save in globals vars of class
        SatelliteData.satellite = self.satellite
        SatelliteData.shortname = self.shortname
        SatelliteData.tile = self.tile

        self.set_quality_control_bands()
        del tree

    def set_quality_control_bands(self):
        """Create all quality control bands class (ModisQC)
        based on the type of MODIS products. Create one
        Modis quality control (ModisQC) for each quality
        control band of this satellite data instance.
        """

        self.qc_bands = {}

        # for MOD09/MYD09 A1 (Collection 6)
        if self.shortname in ['MOD09A1', 'MYD09A1']:
            # define numbers of bits for the band value in binary

            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if '_qc_' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name, num_bits=32)
            # Solar Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'szen' in x[1]][0][0]
            self.qc_bands['sza'] = ModisQC(self.shortname, 'sza', qc_name)
            # View/Sensor Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'vzen' in x[1]][0][0]
            self.qc_bands['vza'] = ModisQC(self.shortname, 'vza', qc_name)
            # Relative Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'raz' in x[1]][0][0]
            self.qc_bands['rza'] = ModisQC(self.shortname, 'rza', qc_name)
            # Reflectance State QA flags
            qc_name = [x for x in self.sub_datasets if '_state_' in x[1]][0][0]
            self.qc_bands['sf'] = ModisQC(self.shortname, 'sf', qc_name, num_bits=16)

        # for MOD09/MYD09 Q1 (Collection 6)
        if self.shortname in ['MOD09Q1', 'MYD09Q1']:
            # Reflectance State QA flags
            qc_name = [x for x in self.sub_datasets if '_state_' in x[1]][0][0]
            self.qc_bands['sf'] = ModisQC(self.shortname, 'sf', qc_name, num_bits=16)
            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if '_qc_' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name, num_bits=16)

        # for MOD09/MYD09 GA (Collection 6)
        if self.shortname in ['MOD09GA', 'MYD09GA']:
            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if 'QC_500m' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name, num_bits=32)
            # Reflectance State QA flags at 1km
            qc_name = [x for x in self.sub_datasets if 'state_1km' in x[1]][0][0]
            self.qc_bands['sf'] = ModisQC(self.shortname, 'sf', qc_name, num_bits=16, scale_resolution=0.5)
            # Solar Zenith Angle at 1km
            qc_name = [x for x in self.sub_datasets if 'SolarZenith' in x[1]][0][0]
            self.qc_bands['sza'] = ModisQC(self.shortname, 'sza', qc_name, scale_resolution=0.5)
            # View/Sensor Zenith Angle at 1km
            qc_name = [x for x in self.sub_datasets if 'SensorZenith' in x[1]][0][0]
            self.qc_bands['vza'] = ModisQC(self.shortname, 'vza', qc_name, scale_resolution=0.5)

        # for MOD09/MYD09 GQ (Collection 6)
        if self.shortname in ['MOD09GQ', 'MYD09GQ']:
            # open datasets from MXD09GA for get some QC in this file
            mxd09ga_file = os.path.abspath(self.file).replace('D09GQ', 'D09GA')
            if not os.path.isfile(mxd09ga_file):
                raise OSError("File not found {0}. For make the quality control of MXD09GQ "
                              "you need have MXD09GA files".format(mxd09ga_file))
            gdal_dataset = gdal.Open(mxd09ga_file, gdal.GA_ReadOnly)
            mxd09ga_sub_datasets = gdal_dataset.GetSubDatasets()
            del gdal_dataset
            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if 'QC_250m' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name, num_bits=16)
            # Reflectance State QA flags from MXD09GA at 1km
            qc_name = [x for x in mxd09ga_sub_datasets if 'state_1km' in x[1]][0][0]
            self.qc_bands['sf'] = ModisQC(self.shortname, 'sf', qc_name, num_bits=16, scale_resolution=0.25)
            # Solar Zenith Angle at 1km
            qc_name = [x for x in mxd09ga_sub_datasets if 'SolarZenith' in x[1]][0][0]
            self.qc_bands['sza'] = ModisQC(self.shortname, 'sza', qc_name, scale_resolution=0.25)
            # View/Sensor Zenith Angle at 1km
            qc_name = [x for x in mxd09ga_sub_datasets if 'SensorZenith' in x[1]][0][0]
            self.qc_bands['vza'] = ModisQC(self.shortname, 'vza', qc_name, scale_resolution=0.25)

    def get_data_band(self, band):
        """Return the raster of the data band for respective band
        of the file.

        :param band: band to process
        :type band: int
        :return: raster of the data band
        :rtype: ndarray
        """

        # TODO: optimize/performance the table open/access in memory (pytables?)

        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name, gdal.GA_ReadOnly)
        data_band_raster = gdal_data_band.ReadAsArray()
        del gdal_data_band
        return data_band_raster

    def get_cols(self, band):
        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name, gdal.GA_ReadOnly)
        return gdal_data_band.RasterXSize

    def get_rows(self, band):
        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name, gdal.GA_ReadOnly)
        return gdal_data_band.RasterYSize

    def get_total_pixels(self, band):
        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name, gdal.GA_ReadOnly)
        return gdal_data_band.RasterXSize*gdal_data_band.RasterYSize

    def get_nodata_value(self, band):
        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name, gdal.GA_ReadOnly)
        return gdal_data_band.GetRasterBand(1).GetNoDataValue()

    def get_quality_control_bands(self, band):
        return [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
