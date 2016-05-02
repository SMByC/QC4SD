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
import argparse
import gc

from qc4sd.quality_control.quality_control import QualityControl
from qc4sd.quality_control.quality_control_file import setup_quality_control_file
from qc4sd.satellite_data.satellite_data import load_satellite_data, SatelliteData

BASE_DIR = os.path.dirname(__file__)
DEFAULT_QCF = os.path.join(BASE_DIR, 'quality_control', 'qc_default_modis_settings.ini')
#DEFAULT_QCF = os.path.join(BASE_DIR, 'quality_control', 'qc_default_landsat_settings.ini')


def run(qcf, bands, files, output):
    """Main process, execute directly if imported as module.

        >>> from qc4sd import qc4sd
        >>> qc4sd.run(settings.ini, 1, [file1, file2])

    :param qcf: quality control file or 'default'
    :type qcf: str
    :param bands: band or bands to process
    :type bands: list
    :param files: files to process
    :type files: list
    :param output: output directory for save results
    :type output: str
    """

    ################################
    # check parameters

    # quality control file
    if not qcf == 'default' and not os.path.isfile(qcf):
        raise FileNotFoundError("The quality control file not exist, set"
                                " the correct qfc or set 'default' for default "
                                " quality control configuration.")
    if qcf == 'default':
        qcf = DEFAULT_QCF

    # if pass one band as integer, like 1 not as list
    if isinstance(bands, int):
        bands = [bands]

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
    # xml files
    xml_files = [file + ".xml" for file in files]
    for xml_file in xml_files:
        if not os.path.isfile(xml_file):
            raise FileNotFoundError("The xml file {0} not exist.".format(xml_file))
    # output
    if not os.path.isdir(output):
        raise NotADirectoryError("The output directory {0} not exist.".format(output))

    config_run = {'qcf': qcf, 'bands': bands, 'files': files, 'xml_files': xml_files, 'output': output}

    ################################
    # init message

    print("\nQC4SD - Quality Control Algorithm for Satellite Data")
    print("\nConfiguration run:")
    print("\tquality control file: {0}".format(os.path.basename(config_run['qcf'])))
    print("\timages to process: {0}".format(len(config_run['files'])))
    print("\tband(s) to process: {0}".format(','.join([str(b) for b in config_run['bands']])))

    ################################
    # process

    # setup and set the input or default quality control file
    config_run['quality_control_file'] = setup_quality_control_file(config_run['qcf'])

    # load all input files and setup data
    load_satellite_data(config_run)

    # process the quality control per band and save result
    for band in bands:
        qc = QualityControl(config_run['quality_control_file'], band)
        qc.process()
        qc.save_results(config_run['output'])
        qc.save_statistics(config_run['output'])

    # Cleanup
    del config_run, files, qc
    SatelliteData.list = []
    QualityControl.list = []
    # force run garbage collector memory
    gc.collect()


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
    parser.add_argument('-bands', type=str, help='band or bands to process', required=True)
    parser.add_argument('-output', type=str, help='output directory for save results', default=os.getcwd())
    parser.add_argument('files', type=str, help='files to process', nargs='*')

    args = parser.parse_args()

    # formatted the bands argument
    try:
        args.bands = [int(b) for b in list(args.bands.split(','))]
    except:
        raise ValueError("Incorrect format or error value for 'bands', this should be"
                         " band (int) or bands comma separated without space.")

    run(args.qcf, args.bands, args.files, args.output)

    ################################
    # end message
    print("\nCopyright (c) 2015 SMBYC-IDEAM")
    print("Instituto de Hidrología, Meteorología y Estudios Ambientales")
    print("Sistema de Monitoreo de Bosques y Carbono - SMBYC")


if __name__ == '__main__':
    script()
