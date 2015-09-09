#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import os
import osr
import numpy as np
from osgeo import gdal

from QC4SD.lib import fix_zeros
from QC4SD.satellite_data.satellite_data import SatelliteData


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
        self.output_bands = []
        self.output_filename = "{0}_{1}_band{2}.hdf".format(SatelliteData.tile, SatelliteData.shortname, fix_zeros(band, 2))

    def __str__(self):
        return self.band_name

    def process(self):
        """Process the quality control, this is check pixel per pixel
        for specific band to process for all input files. Save all
        raster 2d array checked (QC) sorted chronologically by date
        of input file.
        """

        # for each file
        for sd in self.SatelliteData_list:
            # get raster for band to process
            data_band_raster = sd.get_data_band(self.band)
            # get NoData value specific per band/product
            nodata_value = sd.get_nodata_value(self.band)

            # process each pixel for the band to process
            for (x, y), data_band_pixel in np.ndenumerate(data_band_raster):
                # if pixel is not valid then don't check it
                if data_band_pixel == int(nodata_value): # or True:
                    continue
                # check pixel with all items of all quality control bands configured
                pixel_check_list = {}
                for qc_id_name, qc_checker in sd.qc_bands.items():
                    pixel_check_list[qc_checker.full_name] = qc_checker.quality_control_check(x, y, self.band, self.qcf)

                # the pixel pass or not pass the quality control:
                # check if all validate quality control for this pixel are True
                pixel_pass_quality_control = not (False in [j for sublist in [list(i.values()) for i in list(pixel_check_list.values())] for j in sublist])

                # save check lists of quality control per pixel
                #self.qc_check_lists[(x, y)] = pixel_check_list  # memory leak

                if y == 0:
                    print(x,y,pixel_pass_quality_control)

                # if the pixel not pass the quality control, replace with NoData value
                if not pixel_pass_quality_control:
                    data_band_raster[x, y] = nodata_value

            #print(self.qc_check_lists)

            # save raster band for each input file with QC in sorted list chronologically
            self.output_bands.append(data_band_raster)

    def save_results(self, output_dir):
        # get gdal properties of one of data band
        sd = self.SatelliteData_list[0]
        data_band_name = [x for x in sd.sub_datasets if 'b'+fix_zeros(self.band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name)
        geotransform = gdal_data_band.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        cols = gdal_data_band.RasterXSize
        rows = gdal_data_band.RasterYSize

        # settings projection and output raster
        driver = gdal.GetDriverByName('NETCDF')
        nbands = len(self.output_bands)
        outRaster = driver.Create(os.path.join(output_dir, self.output_filename), cols, rows, nbands, gdal.GDT_Int16)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromWkt(gdal_data_band.GetProjectionRef())
        outRaster.SetProjection(outRasterSRS.ExportToWkt())

        # write bands
        for nband, data_band_raster in enumerate(self.output_bands):
            outband = outRaster.GetRasterBand(nband + 1)
            outband.WriteArray(data_band_raster)
            #outband.WriteArray(sd.get_data_band(self.band))
            outband.FlushCache()


