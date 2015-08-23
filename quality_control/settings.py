#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import os
import configparser
from satellite_data import satellite_data


def quality_control_config(config_file):

    config = configparser.RawConfigParser()
    config.read(config_file)

    return config


def load_input_files(files):

    # check number of files
    if len(files) == 0:  # TODO >1 ??
        raise ValueError("Not files to process")

    # create new instances of satellite data
    satellite_data_list =[]
    for file in files:
        satellite_data_list.append(satellite_data.new(file))

    def check():
        # check all files are the same platform (and satellite),
        # are from same instrument and are in the same tile

        satellite = [sd.satellite for sd in satellite_data_list]
        if not all(x == satellite[0] for x in satellite):
            raise ValueError("All files aren't in the same platform")

        subproduct = [sd.shortname for sd in satellite_data_list]
        if not all(x == subproduct[0] for x in subproduct):
            raise ValueError("All files aren't the same type of subproduct")

        tile = [sd.tile for sd in satellite_data_list]
        if not all(x == tile[0] for x in tile):
            raise ValueError("All files aren't in the same tile")

    check()


# from osgeo import gdal
#
# gdal_dataset = gdal.Open(
#     "/multimedia/Tmp_build/ATD_data/Quality_Control/p0_download/MOD09A1/h10v07/MOD09A1.A2014361.h10v07.005.2015006072800.hdf")
#
# print(gdal_dataset.GetSubDatasets())
#
# shortname = gdal_dataset.GetMetadataItem('SHORTNAME')
#
# for x in gdal_dataset.GetSubDatasets(): print(x[1])
#
# qc = gdal.Open(
#     'HDF4_EOS:EOS_GRID:"/multimedia/Tmp_build/ATD_data/Quality_Control/p0_download/MOD09A1/h10v07/MOD09A1.A2014361.h10v07.005.2015006072800.hdf":MOD_Grid_500m_Surface_Reflectance:sur_refl_qc_500m')

