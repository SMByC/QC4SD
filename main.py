#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright © 2015, SMBYC - IDEAM
# Author: Xavier Corredor Llano <xcorredorl@ideam.gov.co>


from osgeo import gdal

gdal_dataset = gdal.Open("/multimedia/Tmp_build/ATD_data/Quality_Control/p0_download/MOD09A1/h10v07/MOD09A1.A2014361.h10v07.005.2015006072800.hdf")

print gdal_dataset.GetSubDatasets()

shortname = gdal_dataset.GetMetadataItem('SHORTNAME')

for x in gdal_dataset.GetSubDatasets(): print x[1]

qc = gdal.Open('HDF4_EOS:EOS_GRID:"/multimedia/Tmp_build/ATD_data/Quality_Control/p0_download/MOD09A1/h10v07/MOD09A1.A2014361.h10v07.005.2015006072800.hdf":MOD_Grid_500m_Surface_Reflectance:sur_refl_qc_500m')

print qc.ReadAsArray()