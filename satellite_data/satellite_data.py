#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from osgeo import gdal


class SatelliteData:

    def __init__(self, file, satellite_instrument):
        self.file = file
        self.satellite_instrument = satellite_instrument

    def setup_metadata(self):
        pass


def new(file):
    """Create new instance of child of SatelliteData class
    (ModisFile, LandsatFile, ...) base on metadata of input
    file

    :param file: input file
    :type file: str
    :return: child of SatelliteData
    :rtype: SatelliteData
    """

    dataset = gdal.Open(file)
    satellite_instrument = dataset.GetMetadata()["ASSOCIATEDINSTRUMENTSHORTNAME"]

    if satellite_instrument == 'MODIS':
        from satellite_data.modis import ModisFile
        new_modis = ModisFile(file, dataset)

        return new_modis