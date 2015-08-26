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

from QC4SD.quality_control.quality_control import QualityControl
from QC4SD.quality_control.quality_control_file import setup_quality_control_file
from QC4SD.satellite_data.satellite_data import load_satellite_data, SatelliteData

BASE_DIR = os.path.dirname(__file__)
DEFAULT_QCF = os.path.join(BASE_DIR, 'quality_control', 'qc_default_settings.ini')


def run(qcf, bands, files, output):
    """Main process, execute directly if imported as module.

        >>> from QC4SD import qc4sd
        >>> qc4sd.run(settings.ini, 1, [file1, file2])

    :param qcf: quality control file or 'default'
    :type qcf: str
    :param bands: bands to process for the input files
    :type bands: list
    :param files: files to process
    :type files: list
    :param output: output directory for save results
    :type output: str
    """

    ########################
    # check parameters

    # quality control file
    if not qcf == 'default' and not os.path.isfile(qcf):
        raise FileNotFoundError("The quality control file not exist, set"
                                " the correct qfc or set 'default' for default "
                                " quality control configuration.")
    if qcf == 'default':
        qcf = DEFAULT_QCF
    # bands
    try:
        bands = [int(b) for b in bands]
    except:
        raise ValueError("Incorrect format or error value for 'bands', this should be"
                         " a list (int) of band or bands.")
    # files
    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError("The file {0} not exist.".format(file))
    # output
    if not os.path.isdir(output):
        raise NotADirectoryError("The output directory not exist.")

    config_run = {'qcf': qcf, 'bands': bands, 'files': files, 'output': output}

    print(config_run)

    ########################
    # process

    # setup and set the input or default quality control file
    config_run['quality_control_file'] = setup_quality_control_file(config_run['qcf'])

    # load all input files and setup data
    load_satellite_data(config_run)

    # process the quality control per band and save result
    for band in bands:
        qc = QualityControl(SatelliteData.list, config_run['quality_control_file'], band)
        qc.process()
        qc.save_results(config_run['output'])


def script():
    """Execute only if run as a script.

        $ python3 qc4sd.py -qcf settings.ini -band 1 file1 file2
    """

    # Create parser arguments
    parser = argparse.ArgumentParser(
        prog='qc4sd',
        description='Quality control algorithm for satellite data',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-qcf', type=str, help='quality control file', required=True)
    parser.add_argument('-bands', type=str, help='band or bands to process for the input files', required=True)
    parser.add_argument('files', type=str, help='files to process', nargs='*')
    parser.add_argument('-output', type=str, help='output directory for save results', default=os.getcwd())

    args = parser.parse_args()


    # formatted the bands argument
    try:
        args.bands = [int(b) for b in list(args.bands.split(','))]
    except:
        raise ValueError("Incorrect format or error value for 'bands', this should be"
                         " band (int) or bands comma separated without space.")

    run(args.qcf, args.bands, args.files, args.output)


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