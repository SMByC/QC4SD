#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015-2016
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from qc4sd.lib import fix_binary_string, int2bin


# [MXD09GQ] ########################################################
# for MOD09GQ and MYD09GQ (Collection 6)

#### Reflectance Band Quality (rbq) ####
def rbq(modis_qc, qcf, band, qc_pixel_value):
    pixel_pass_quality_control = True
    # prepare data
    qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), modis_qc.num_bits)
    ### Modland QA
    bits = qc_bin_str[0:2]
    if qcf.getboolean('MXD09GQ', 'rbq_modland_qa_' + bits) is False:
        modis_qc.invalid_pixels['rbq_modland_qa_' + bits] += 1
        pixel_pass_quality_control = False
    ### Data Quality
    bits = qc_bin_str[(band - 1) * 4 + 4:band * 4 + 4]
    if qcf.getboolean('MXD09GQ', 'rbq_data_quality_' + bits) is False:
        modis_qc.invalid_pixels['rbq_data_quality_' + bits] += 1
        pixel_pass_quality_control = False
    ### Atmospheric correction
    qc_pixel_value = qc_bin_str[12]
    if (qcf.getboolean('MXD09GQ', 'rbq_atcorr_0') or bool(int(qc_pixel_value))) is False:
        modis_qc.invalid_pixels['rbq_atcorr_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09GQ', 'rbq_atcorr_1'):
        modis_qc.invalid_pixels['rbq_atcorr_1'] += 1
        pixel_pass_quality_control = False
    ### Adjacency correction
    qc_pixel_value = qc_bin_str[13]
    if (qcf.getboolean('MXD09GQ', 'rbq_adjcorr_0') or bool(int(qc_pixel_value))) is False:
        modis_qc.invalid_pixels['rbq_adjcorr_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09GQ', 'rbq_adjcorr_1'):
        modis_qc.invalid_pixels['rbq_adjcorr_1'] += 1
        pixel_pass_quality_control = False

    return pixel_pass_quality_control
