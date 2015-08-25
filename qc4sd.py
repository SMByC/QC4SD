#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Quality control algorithm for satellite data
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co
#
##################################################################
#
#  Licence..
#
##################################################################

import os
import sys
import argparse

from quality_control.settings import quality_control_config
from quality_control.process import main as process_of_quality_control
from satellite_data.satellite_data import load_satellite_data

BASE_DIR = os.path.dirname(__file__)
DEFAULT_QCF = os.path.join(BASE_DIR, 'quality_control', 'qc_default_settings.ini')


def run(qcf, band, files):
    """Execute directly if imported as module.

        >>> from QC4SD import qc4sd
        >>> qc4sd.run(settings.ini, 1, [file1, file2])

    :param qcf: quality control file or 'default'
    :type qcf: str
    :param band: band to process
    :type band: int
    :param files: files to process
    :type files: list
    """

    if qcf == 'default':
        qcf = DEFAULT_QCF

    config_run = {'qcf': qcf, 'band': band, 'files': files}

    print(config_run)

    config_run['quality_control'] = quality_control_config(config_run['qcf'])

    print(config_run['quality_control'])
    print(config_run['quality_control'].sections())

    # load all input files and setup data
    SatelliteDataList = load_satellite_data(config_run)

    # process ...
    process_of_quality_control(SatelliteDataList)


def script():
    """Execute only if run as a script.

        $ python3 qc4sd.py -qcf settings.ini -band 1 file1 file2
    """

    # Create parser arguments
    parser = argparse.ArgumentParser(
        prog='qc4sd',
        description='Quality control algorithm for satellite data',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-qcf', type=str, help='Quality Control File', required=True)
    parser.add_argument('-band', type=int, help='Band to process', required=True)
    parser.add_argument('files', type=str, help='Files to process', nargs='*')

    args = parser.parse_args()

    run(args.qcf, args.band, args.files)


if __name__ == '__main__':
    script()


'''

from osgeo import gdal

gdal_dataset = gdal.Open(
    "/multimedia/Tmp_build/ATD_data/Quality_Control/p0_download/MOD09A1/h10v07/MOD09A1.A2014361.h10v07.005.2015006072800.hdf")

print(gdal_dataset.GetSubDatasets())

shortname = gdal_dataset.GetMetadataItem('SHORTNAME')

for x in gdal_dataset.GetSubDatasets(): print(x[1])

qc = gdal.Open(
    'HDF4_EOS:EOS_GRID:"/multimedia/Tmp_build/ATD_data/Quality_Control/p0_download/MOD09A1/h10v07/MOD09A1.A2014361.h10v07.005.2015006072800.hdf":MOD_Grid_500m_Surface_Reflectance:sur_refl_qc_500m')

print(qc.ReadAsArray())
'''