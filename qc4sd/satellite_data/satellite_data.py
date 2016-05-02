#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015-2016
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import os
import xml.etree.ElementTree as ET
try:
    from osgeo import gdal
except ImportError:
    import gdal


class SatelliteData:
    """Generic and parent class for satellite data, this
    contain the basic instructions, variables and functions.
    This need to be inherit from specialize class, such as,
    Modis or Landsat
    """

    # static fields (globals)
    satellite = None
    shortname = None
    tile = None

    # save all instances
    list = []

    def __init__(self, file):
        self.satellite_instrument = self.__class__.__name__
        self.file = file
        self.file_name = os.path.basename(file)

        gdal_dataset = gdal.Open(file)
        self.sub_datasets = gdal_dataset.GetSubDatasets()
        del gdal_dataset

    def __str__(self):
        return self.file_name


def new(file, xml_file):
    """Create new instance of child of SatelliteData class
    (MODIS, LandsatFile, ...) base on metadata of input
    file.

    :param xml_file: input xml file
    :type xml_file: str
    :param file: input file
    :type file: str
    """

    tree = ET.parse(xml_file)
    satellite_instrument = list(tree.iter('SensorShortName'))[0].text
    del tree

    if satellite_instrument == 'MODIS':
        from qc4sd.satellite_data.modis import MODIS
        MODIS(file, xml_file)
    elif satellite_instrument == 'LANDSAT':
        pass
    else:
        raise NotImplementedError("Product {0} not implemented or not supported".format(satellite_instrument))


def load_satellite_data(config_run):
    """Read and load all satellite data from files
    """

    # check number of files
    if len(config_run['files']) == 0:
        raise ValueError("Not files to process")

    # create new instances of satellite data

    for file, xml_file in zip(config_run['files'], config_run['xml_files']):
        new(file, xml_file)

    def check():
        # check all files are the same platform (and satellite),
        # are from same instrument and are in the same tile

        satellite = [sd.satellite for sd in SatelliteData.list]
        if not all(x == satellite[0] for x in satellite):
            raise ValueError("All files aren't in the same platform")

        subproduct = [sd.shortname for sd in SatelliteData.list]
        if not all(x == subproduct[0] for x in subproduct):
            raise ValueError("All files aren't the same type of subproduct")

        tile = [sd.tile for sd in SatelliteData.list]
        if not all(x == tile[0] for x in tile):
            raise ValueError("All files aren't in the same tile")
    check()


