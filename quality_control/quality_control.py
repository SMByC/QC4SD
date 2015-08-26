#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import numpy
from osgeo import gdal

from QC4SD.satellite_data.satellite_data import SatelliteData


class QualityControl:

    # save all instances
    list = []

    def __init__(self, satellite_data, quality_control_file):
        QualityControl.list.append(self)

        self.satellite_data = satellite_data
        self.quality_control_file = quality_control_file

    def __str__(self):
        return self.file_name

    def process(self):
        # get raster for band to process
        gdal_dataset_band = gdal.Open(satellite_data.band_name)
        band_to_process_raster = gdal_dataset_band.ReadAsArray()

        # get raster for quality control band
        gdal_dataset_qc = gdal.Open(satellite_data.qc_name)
        quality_control_raster = gdal_dataset_qc.ReadAsArray()

        # process each pixel for the band to process and quality control band
        for (x, y), band_value in numpy.ndenumerate(band_to_process_raster):
            qc_value = quality_control_raster.item((x, y))
            print(x,y,band_value, qc_value)

        del gdal_dataset_band
        del gdal_dataset_qc
        del band_to_process_raster
        del quality_control_raster


def process():

    # sorted the satellite input data files by date (chronological order)
    SatelliteData.list.sort(key=lambda x: x.datetime)

    for satellite_data in SatelliteData.list:
        print(satellite_data)
        print(satellite_data.datetime)

    # process each file (tile)
    for satellite_data in SatelliteData.list:
        # get raster for band to process
        gdal_dataset_band = gdal.Open(satellite_data.band_name)
        band_to_process_raster = gdal_dataset_band.ReadAsArray()

        # get raster for quality control band
        gdal_dataset_qc = gdal.Open(satellite_data.qc_name)
        quality_control_raster = gdal_dataset_qc.ReadAsArray()

        # process each pixel for the band to process and quality control band
        for (x, y), band_value in numpy.ndenumerate(band_to_process_raster):
            qc_value = quality_control_raster.item((x, y))
            print(x,y,band_value, qc_value)





        del gdal_dataset_band
        del gdal_dataset_qc
        del band_to_process_raster
        del quality_control_raster
