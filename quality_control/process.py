#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import numpy
from osgeo import gdal

def main(SatelliteDataList):

    # sorted the satellite input data files by date (chronological order)
    SatelliteDataList.sort(key=lambda x: x.datetime)

    for SatelliteData in SatelliteDataList:
        print(SatelliteData)
        print(SatelliteData.datetime)

    # process each file (tile)
    for SatelliteData in SatelliteDataList:
        # get raster for band to process
        gdal_dataset_band = gdal.Open(SatelliteData.band_name)
        band_to_process_raster = gdal_dataset_band.ReadAsArray()

        # get raster for quality control band
        gdal_dataset_qc = gdal.Open(SatelliteData.qc_name)
        quality_control_raster = gdal_dataset_qc.ReadAsArray()

        # process each pixel for the band to process and quality control band
        for (x, y), band_value in numpy.ndenumerate(band_to_process_raster):
            qc_value = quality_control_raster.item((x, y))
            print(x,y,band_value, qc_value)





        del gdal_dataset_band
        del gdal_dataset_qc
        del band_to_process_raster
        del quality_control_raster
