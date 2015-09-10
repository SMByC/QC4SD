#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from osgeo import gdal

from QC4SD.lib import fix_binary_string, int2bin


class ModisQC:
    """Quality control class for MODIS files. One instance represent
    one band of quality control for specific type of MODIS products.
    Each type of MODIS products has different bands of quality control
    and rules for check the quality control for one pixel.
    """

    def __init__(self, sd_shortname, id_name, qc_name, num_bits=None):
        self.sd_shortname = sd_shortname
        self.id_name = id_name
        self.qc_name = qc_name
        self.num_bits = num_bits
        # get raster for quality control band
        gdal_dataset_qc = gdal.Open(self.qc_name)
        self.quality_control_raster = gdal_dataset_qc.ReadAsArray()
        del gdal_dataset_qc

        self.setup()

    def setup(self):
        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:
            if self.id_name == 'rbq': self.full_name = 'Reflectance Band Quality'
            if self.id_name == 'sza': self.full_name = 'Solar Zenith Angle'
            if self.id_name == 'vza': self.full_name = 'View Zenith Angle'
            if self.id_name == 'rza': self.full_name = 'Relative Zenith Angle'
            if self.id_name == 'sf':  self.full_name = 'State flags'

    def quality_control_check(self, x, y, band, qcf):
        """Check if the specific pixel in x and y position pass or not
        pass all quality controls, this is evaluate with the quality
        control value for the respective pixel position. The quality
        controls is evaluate based on the quality control file.

        :param x: raster position in x for the pixel
        :type x: int
        :param y: raster position in y for the pixel
        :type y: int
        :param band: band of data to process
        :type band: int
        :param qcf: quality control file
        :type qcf: 
        :return: check list
        :rtype: dict
        """

        # get the pixel value for specific band of quality control
        qc_pixel_value = self.quality_control_raster.item((x, y))

        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:

            #### Reflectance Band Quality (rbq) ####
            def rbq(qc_pixel_value):
                # for save all check quality control items
                pixel_check_list = {}
                # prepare data
                qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), self.num_bits)
                ### Modland QA
                bits = qc_bin_str[0:2]
                pixel_check_list['rbq_modland_qa_'+bits] = qcf.getboolean('MXD09A1', 'rbq_modland_qa_'+bits)
                ### Data Quality
                bits = qc_bin_str[(band-1)*4+2:band*4+2]
                pixel_check_list['rbq_data_quality_'+bits] = qcf.getboolean('MXD09A1', 'rbq_data_quality_'+bits)
                ### Atmospheric correction
                qc_pixel_value = qc_bin_str[30]
                pixel_check_list['rbq_atcorr_0'] = qcf.getboolean('MXD09A1', 'rbq_atcorr_0') or bool(int(qc_pixel_value))
                pixel_check_list['rbq_atcorr_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'rbq_atcorr_1')) else True
                ### Adjacency correction
                qc_pixel_value = qc_bin_str[31]
                pixel_check_list['rbq_adjcorr_0'] = qcf.getboolean('MXD09A1', 'rbq_adjcorr_0') or bool(int(qc_pixel_value))
                pixel_check_list['rbq_adjcorr_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'rbq_adjcorr_1')) else True

                return pixel_check_list

            #### Solar Zenith Angle Band ####
            def sza(qc_pixel_value):
                # for save all check quality control items
                pixel_check_list = {}
                # prepare data
                qc_scale_factor = 0.01
                qc_pixel_value = float(qc_pixel_value)*qc_scale_factor
                ### Check
                pixel_check_list['szangle_min'] = qc_pixel_value >= qcf.getfloat('MXD09A1', 'szangle_min')
                pixel_check_list['szangle_max'] = qc_pixel_value <= qcf.getfloat('MXD09A1', 'szangle_max')

                return pixel_check_list

            #### View Zenith Angle Band ####
            def vza(qc_pixel_value):
                # for save all check quality control items
                pixel_check_list = {}
                # prepare data
                qc_scale_factor = 0.01
                qc_pixel_value = float(qc_pixel_value)*qc_scale_factor
                ### Check
                pixel_check_list['vzangle_min'] = qc_pixel_value >= qcf.getfloat('MXD09A1', 'vzangle_min')
                pixel_check_list['vzangle_max'] = qc_pixel_value <= qcf.getfloat('MXD09A1', 'vzangle_max')

                return pixel_check_list

            #### Relative Zenith Angle Band ####
            def rza(qc_pixel_value):
                # for save all check quality control items
                pixel_check_list = {}
                # prepare data
                qc_scale_factor = 0.01
                qc_pixel_value = float(qc_pixel_value)*qc_scale_factor
                ### Check
                pixel_check_list['rzangle_min'] = qc_pixel_value >= qcf.getfloat('MXD09A1', 'rzangle_min')
                pixel_check_list['rzangle_max'] = qc_pixel_value <= qcf.getfloat('MXD09A1', 'rzangle_max')

                return pixel_check_list

            #### State flags Band (sf) ####
            def sf(qc_pixel_value):
                # for save all check quality control items
                pixel_check_list = {}
                # prepare data
                qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), self.num_bits)
                ### Cloud State
                bits = qc_bin_str[0:2]
                pixel_check_list['sf_cloud_state_'+bits] = qcf.getboolean('MXD09A1', 'sf_cloud_state_'+bits)
                ### Cloud shadow
                qc_pixel_value = qc_bin_str[2]
                pixel_check_list['sf_cloud_shadow_0'] = qcf.getboolean('MXD09A1', 'sf_cloud_shadow_0') or bool(int(qc_pixel_value))
                pixel_check_list['sf_cloud_shadow_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_cloud_shadow_1')) else True
                ### Land/Water flag
                bits = qc_bin_str[3:6]
                pixel_check_list['sf_land_water_'+bits] = qcf.getboolean('MXD09A1', 'sf_land_water_'+bits)
                ### Aerosol Quantity
                bits = qc_bin_str[6:8]
                pixel_check_list['sf_aerosol_quantity_'+bits] = qcf.getboolean('MXD09A1', 'sf_aerosol_quantity_'+bits)
                ### cirrus_detected
                bits = qc_bin_str[8:10]
                pixel_check_list['sf_cirrus_detected_'+bits] = qcf.getboolean('MXD09A1', 'sf_cirrus_detected_'+bits)
                ### Internal Cloud Algorithm Flag
                qc_pixel_value = qc_bin_str[10]
                pixel_check_list['sf_internal_cloud_algorithm_0'] = qcf.getboolean('MXD09A1', 'sf_internal_cloud_algorithm_0') or bool(int(qc_pixel_value))
                pixel_check_list['sf_internal_cloud_algorithm_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_internal_cloud_algorithm_1')) else True
                ### Internal Fire Algorithm Flag
                qc_pixel_value = qc_bin_str[11]
                pixel_check_list['sf_internal_fire_algorithm_0'] = qcf.getboolean('MXD09A1', 'sf_internal_fire_algorithm_0') or bool(int(qc_pixel_value))
                pixel_check_list['sf_internal_fire_algorithm_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_internal_fire_algorithm_1')) else True
                ### MOD35 snow/ice flag
                qc_pixel_value = qc_bin_str[12]
                pixel_check_list['sf_mod35_snow_ice_0'] = qcf.getboolean('MXD09A1', 'sf_mod35_snow_ice_0') or bool(int(qc_pixel_value))
                pixel_check_list['sf_mod35_snow_ice_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_mod35_snow_ice_1')) else True
                ### Pixel adjacent to cloud
                qc_pixel_value = qc_bin_str[13]
                pixel_check_list['sf_pixel_adjacent_to_cloud_0'] = qcf.getboolean('MXD09A1', 'sf_pixel_adjacent_to_cloud_0') or bool(int(qc_pixel_value))
                pixel_check_list['sf_pixel_adjacent_to_cloud_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_pixel_adjacent_to_cloud_1')) else True
                ### BRDF correction performed
                qc_pixel_value = qc_bin_str[14]
                pixel_check_list['sf_brdf_correction_performed_0'] = qcf.getboolean('MXD09A1', 'sf_brdf_correction_performed_0') or bool(int(qc_pixel_value))
                pixel_check_list['sf_brdf_correction_performed_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_brdf_correction_performed_1')) else True
                ### Internal Snow Mask
                qc_pixel_value = qc_bin_str[15]
                pixel_check_list['sf_internal_snow_mask_0'] = qcf.getboolean('MXD09A1', 'sf_internal_snow_mask_0') or bool(int(qc_pixel_value))
                pixel_check_list['sf_internal_snow_mask_1'] = False if (bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_internal_snow_mask_1')) else True

                return pixel_check_list

            # switch case for quality control band
            quality_control_band = {
                'rbq': rbq,
                'sza': sza,
                'vza': vza,
                'rza': rza,
                'sf': sf,
            }

            return quality_control_band[self.id_name](qc_pixel_value)

                # TODO Q1

