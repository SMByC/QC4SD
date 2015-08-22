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

import sys
import argparse


def main(config_run):
    print(config_run)
    pass


def run(qcf, band, files):
    # execute only if imported as module
    #
    # from QC4SD import qc4sd
    # qc4sd.run('QC4SD/quality_control/qc_default_settings.ini', 1, 'QC4SD/lib.py')
    config_run = {'qcf': open(qcf, 'r'), 'band': band, 'files': files}
    main(config_run)


def script():
    # execute only if run as a script
    #
    # python3 qc4sd.py -qcf quality_control/qc_default_settings.ini -band 1 *.py

    # Create parser arguments
    parser = argparse.ArgumentParser(
        prog='qc4sd',
        description='Quality control algorithm for satellite data',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-qcf', type=argparse.FileType('r'), help='Quality Control File', required=True)
    parser.add_argument('-band', type=int, help='Band to process', required=True)
    parser.add_argument('files', type=str, help='Files to process', nargs='*')

    args = parser.parse_args()

    config_run = {'qcf': args.qcf, 'band': args.band, 'files': args.files}

    print(config_run)

    main(config_run)


if __name__ == '__main__':
    script()


#
# sys.exit()
#
#
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
#
# print(qc.ReadAsArray())
