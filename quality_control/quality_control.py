#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import numpy
from osgeo import gdal

from QC4SD.lib import fix_zeros


class QualityControl:
    """Process the quality control for all input file for one
    band with the quality control settings based on quality control
    file.
    """

    # save all instances
    list = []

    def __init__(self, SatelliteData_list, quality_control_file, band):
        QualityControl.list.append(self)
        self.band = band
        self.band_name = 'band'+fix_zeros(band, 2)

        self.SatelliteData_list = SatelliteData_list
        self.qcf = quality_control_file

        self.qc_check_lists = {}

        self.output_driver = None
        self.output_raster = None   # copy matrix, only delete no passed pixel

    def __str__(self):
        return self.band_name

    def process(self):
        # for each file
        for sd in self.SatelliteData_list:
            # get raster for band to process
            data_band_raster = sd.get_data_band(self.band)

            # process each pixel for the band to process
            for (x, y), data_band_pixel in numpy.ndenumerate(data_band_raster):
                # check pixel with all items of all quality control bands configured
                for qc_id_name, qc_checker in sd.qc_bands.items():
                    self.qc_check_lists[qc_checker.full_name] = qc_checker.quality_control_check(x, y, self.band, self.qcf)




                # TODO
                if "all values in self.qc_check_lists are true":
                    save_pixel(data_band_pixel)
                else:
                    save_pixel(float('nan'))



            del data_band_raster




    def save_results(self, output_dir):
        pass


def process2():

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
