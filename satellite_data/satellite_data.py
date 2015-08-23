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
    file.

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


def load_satellite_data(config_run):

    # check number of files
    if len(config_run['files']) == 0:  # TODO >1 ??
        raise ValueError("Not files to process")

    # create new instances of satellite data
    SatelliteDataList = []
    for file in config_run['files']:
        SatelliteDataList.append(new(file))

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

    # setup the band to process and band of quality control
    for sd in SatelliteDataList:
        # set the band to process
        sd.set_band_to_process(config_run['band'])
        # set the band of quality control
        sd.set_quality_control_band()

    return SatelliteDataList