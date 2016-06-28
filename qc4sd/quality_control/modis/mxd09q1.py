#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015-2016
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from qc4sd.lib import fix_binary_string, int2bin


# [MXD09Q1] ########################################################
# for MOD09Q1 and MYD09Q1 (Collection 6)

#### Reflectance State QA Flags Band (sf) ####
def sf(modis_qc, qcf, band, qc_pixel_value, with_stats):
    pixel_pass_quality_control = True
    # prepare data
    qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), modis_qc.num_bits)
    ### Cloud State
    bits = qc_bin_str[0:2]
    if qcf.getboolean('MXD09Q1', 'sf_cloud_state_' + bits) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_cloud_state_' + bits] += 1
        pixel_pass_quality_control = False
    ### Cloud shadow
    qc_pixel_value = qc_bin_str[2]
    if (qcf.getboolean('MXD09Q1', 'sf_cloud_shadow_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_cloud_shadow_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_cloud_shadow_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_cloud_shadow_1'] += 1
        pixel_pass_quality_control = False
    ### Land/Water flag
    bits = qc_bin_str[3:6]
    if qcf.getboolean('MXD09Q1', 'sf_land_water_' + bits) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_land_water_' + bits] += 1
        pixel_pass_quality_control = False
    ### Aerosol Quantity
    bits = qc_bin_str[6:8]
    if qcf.getboolean('MXD09Q1', 'sf_aerosol_quantity_' + bits) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_aerosol_quantity_' + bits] += 1
        pixel_pass_quality_control = False
    ### cirrus_detected
    bits = qc_bin_str[8:10]
    if qcf.getboolean('MXD09Q1', 'sf_cirrus_detected_' + bits) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_cirrus_detected_' + bits] += 1
        pixel_pass_quality_control = False
    ### Internal Cloud Algorithm Flag
    qc_pixel_value = qc_bin_str[10]
    if (qcf.getboolean('MXD09Q1', 'sf_internal_cloud_algorithm_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_internal_cloud_algorithm_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_internal_cloud_algorithm_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_internal_cloud_algorithm_1'] += 1
        pixel_pass_quality_control = False
    ### Internal Fire Algorithm Flag
    qc_pixel_value = qc_bin_str[11]
    if (qcf.getboolean('MXD09Q1', 'sf_internal_fire_algorithm_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_internal_fire_algorithm_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_internal_fire_algorithm_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_internal_fire_algorithm_1'] += 1
        pixel_pass_quality_control = False
    ### MOD35 snow/ice flag
    qc_pixel_value = qc_bin_str[12]
    if (qcf.getboolean('MXD09Q1', 'sf_mod35_snow_ice_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_mod35_snow_ice_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_mod35_snow_ice_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_mod35_snow_ice_1'] += 1
        pixel_pass_quality_control = False
    ### Pixel adjacent to cloud
    qc_pixel_value = qc_bin_str[13]
    if (qcf.getboolean('MXD09Q1', 'sf_pixel_adjacent_to_cloud_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_pixel_adjacent_to_cloud_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_pixel_adjacent_to_cloud_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_pixel_adjacent_to_cloud_1'] += 1
        pixel_pass_quality_control = False
    ### Salt pan
    qc_pixel_value = qc_bin_str[14]
    if (qcf.getboolean('MXD09Q1', 'sf_salt_pan_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_salt_pan_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_salt_pan_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_salt_pan_1'] += 1
        pixel_pass_quality_control = False
    ### Internal Snow Mask
    qc_pixel_value = qc_bin_str[15]
    if (qcf.getboolean('MXD09Q1', 'sf_internal_snow_mask_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_internal_snow_mask_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_internal_snow_mask_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['sf_internal_snow_mask_1'] += 1
        pixel_pass_quality_control = False

    return pixel_pass_quality_control


#### Reflectance Band Quality (rbq) ####
def rbq(modis_qc, qcf, band, qc_pixel_value, with_stats):
    pixel_pass_quality_control = True
    # prepare data
    qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), modis_qc.num_bits)
    ### Modland QA
    bits = qc_bin_str[0:2]
    if qcf.getboolean('MXD09Q1', 'rbq_modland_qa_' + bits) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_modland_qa_' + bits] += 1
        pixel_pass_quality_control = False
    ### Data Quality
    bits = qc_bin_str[(band - 1) * 4 + 4:band * 4 + 4]
    if qcf.getboolean('MXD09Q1', 'rbq_data_quality_' + bits) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_data_quality_' + bits] += 1
        pixel_pass_quality_control = False
    ### Atmospheric correction
    qc_pixel_value = qc_bin_str[12]
    if (qcf.getboolean('MXD09Q1', 'rbq_atcorr_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_atcorr_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'rbq_atcorr_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_atcorr_1'] += 1
        pixel_pass_quality_control = False
    ### Adjacency correction
    qc_pixel_value = qc_bin_str[13]
    if (qcf.getboolean('MXD09Q1', 'rbq_adjcorr_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_adjcorr_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'rbq_adjcorr_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_adjcorr_1'] += 1
        pixel_pass_quality_control = False
    ### Different orbit
    qc_pixel_value = qc_bin_str[14]
    if (qcf.getboolean('MXD09Q1', 'rbq_difforbit_0') or bool(int(qc_pixel_value))) is False:
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_difforbit_0'] += 1
        pixel_pass_quality_control = False
    if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'rbq_difforbit_1'):
        if not with_stats: return False
        modis_qc.invalid_pixels['rbq_difforbit_1'] += 1
        pixel_pass_quality_control = False

    return pixel_pass_quality_control
