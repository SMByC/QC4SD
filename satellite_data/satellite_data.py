#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import os
from osgeo import gdal


class SatelliteData:

    def __init__(self, file_path):
        self.satellite_instrument = self.__class__.__name__
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)

        gdal_dataset = gdal.Open(file_path)
        self.metadata = gdal_dataset.GetMetadata()
        self.sub_datasets = gdal_dataset.GetSubDatasets()
        del gdal_dataset

    def __str__(self):
        return self.file_name


def new(file_path, band):
    """Create new instance of child of SatelliteData class
    (MODIS, LandsatFile, ...) base on metadata of input
    file.

    :param file_path: input file
    :type file_path: str
    :return: child of SatelliteData
    :rtype: SatelliteData
    """

    gdal_dataset = gdal.Open(file_path)
    satellite_instrument = gdal_dataset.GetMetadata()["ASSOCIATEDINSTRUMENTSHORTNAME"]

    if satellite_instrument == 'MODIS':
        from satellite_data.modis import MODIS
        new_modis = MODIS(file_path, band)
        del gdal_dataset
        return new_modis

    raise NotImplementedError("Product {0} not implemented or not supported".format(satellite_instrument))


def load_satellite_data(config_run):

    # check number of files
    if len(config_run['files']) == 0:  # TODO >1 ??
        raise ValueError("Not files to process")

    # create new instances of satellite data
    SatelliteDataList = []
    for file_path in config_run['files']:
        SatelliteDataList.append(new(file_path, config_run['band']))

    def check():
        # check all files are the same platform (and satellite),
        # are from same instrument and are in the same tile

        satellite = [sd.satellite for sd in SatelliteDataList]
        if not all(x == satellite[0] for x in satellite):
            raise ValueError("All files aren't in the same platform")

        subproduct = [sd.shortname for sd in SatelliteDataList]
        if not all(x == subproduct[0] for x in subproduct):
            raise ValueError("All files aren't the same type of subproduct")

        tile = [sd.tile for sd in SatelliteDataList]
        if not all(x == tile[0] for x in tile):
            raise ValueError("All files aren't in the same tile")
    check()

    return SatelliteDataList