#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

try:
    from osgeo import gdal
except ImportError:
    import gdal

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
        # statistics for invalid pixel in respective field
        self.invalid_pixels = {}
        # this quality band need to be check
        self.need_check = True

        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1 (Collection 6)
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:

            # set the full name for this quality control band
            if self.id_name == 'rbq': self.full_name = 'Reflectance Band Quality'
            if self.id_name == 'sza': self.full_name = 'Solar Zenith Angle'
            if self.id_name == 'vza': self.full_name = 'View Zenith Angle'
            if self.id_name == 'rza': self.full_name = 'Relative Zenith Angle'
            if self.id_name == 'sf':  self.full_name = 'Reflectance State QA flags'

        # [MXD09Q1] ########################################################
        # for MOD09Q1 and MYD09Q1 (Collection 6)
        if self.sd_shortname in ['MOD09Q1', 'MYD09Q1']:

            # set the full name for this quality control band
            if self.id_name == 'sf':  self.full_name = 'Reflectance State QA flags'
            if self.id_name == 'rbq': self.full_name = 'Reflectance Band Quality'

    def init_statistics(self, qcf):
        """Configure and initialize statistics values. This need to be
        called for restart statistics for process quality control check
        for each new satellite data.

        :param qcf: quality control file
        :type qcf: configparse
        """
        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:

            # create and init the statistics fields dictionary to zero count value,
            # for specific quality control band (id_name) that belonging this instance
            keys_from_qcf = list(qcf['MXD09A1'].keys())
            self.invalid_pixels = dict((k, 0) for k in keys_from_qcf if k.startswith(self.id_name+'_'))

            # verification if this quality band type need to check:
            # if all items of this qc type in qcf are True, this means
            # that this qc don't need to be check, all pass this qc
            single_qcf_values = set([v for k,v in qcf['MXD09A1'].items() if k.startswith(self.id_name+'_')])
            if len(single_qcf_values) == 1 and single_qcf_values.pop() == 'true':
                self.need_check = False
            if self.id_name == 'sza' or self.id_name == 'vza':
                if qcf.getint('MXD09A1', self.id_name+'_min') == 0 and qcf.getint('MXD09A1', self.id_name+'_max') == 180:
                    self.need_check = False
            if self.id_name == 'rza':
                if qcf.getint('MXD09A1', self.id_name+'_min') == -180 and qcf.getint('MXD09A1', self.id_name+'_max') == 180:
                    self.need_check = False

        # [MXD09Q1] ########################################################
        # for MOD09Q1 and MYD09Q1
        if self.sd_shortname in ['MOD09Q1', 'MYD09Q1']:

            # create and init the statistics fields dictionary to zero count value,
            # for specific quality control band (id_name) that belonging this instance
            keys_from_qcf = list(qcf['MXD09Q1'].keys())
            self.invalid_pixels = dict((k, 0) for k in keys_from_qcf if k.startswith(self.id_name+'_'))

            # verification if this quality band type need to check:
            # if all items of this qc type in qcf are True, this means
            # that this qc don't need to be check, all pass this qc
            single_qcf_values = set([v for k,v in qcf['MXD09Q1'].items() if k.startswith(self.id_name+'_')])
            if len(single_qcf_values) == 1 and single_qcf_values.pop() == 'true':
                self.need_check = False

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
        # pass the qc if this quality band don't need to be check
        if self.need_check is False:
            return True

        # get the pixel value for specific band of quality control
        qc_pixel_value = self.quality_control_raster.item((x, y))

        # [MXD09A1] ########################################################
        # for MOD09A1 and MYD09A1 (Collection 6)
        if self.sd_shortname in ['MOD09A1', 'MYD09A1']:

            # TODO: need work for increase the performance, check qcf if is false before

            #### Reflectance Band Quality (rbq) ####
            def rbq(qc_pixel_value):
                pixel_pass_quality_control = True
                # prepare data
                qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), self.num_bits)
                ### Modland QA
                bits = qc_bin_str[0:2]
                if qcf.getboolean('MXD09A1', 'rbq_modland_qa_'+bits) is False:
                    self.invalid_pixels['rbq_modland_qa_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Data Quality
                bits = qc_bin_str[(band-1)*4+2:band*4+2]
                if qcf.getboolean('MXD09A1', 'rbq_data_quality_'+bits) is False:
                    self.invalid_pixels['rbq_data_quality_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Atmospheric correction
                qc_pixel_value = qc_bin_str[30]
                if (qcf.getboolean('MXD09A1', 'rbq_atcorr_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['rbq_atcorr_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'rbq_atcorr_1'):
                    self.invalid_pixels['rbq_atcorr_1'] += 1
                    pixel_pass_quality_control = False
                ### Adjacency correction
                qc_pixel_value = qc_bin_str[31]
                if (qcf.getboolean('MXD09A1', 'rbq_adjcorr_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['rbq_adjcorr_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'rbq_adjcorr_1'):
                    self.invalid_pixels['rbq_adjcorr_1'] += 1
                    pixel_pass_quality_control = False

                return pixel_pass_quality_control

            #### Solar Zenith Angle Band ####
            def sza(qc_pixel_value):
                pixel_pass_quality_control = True
                # prepare data
                qc_scale_factor = 0.01
                qc_pixel_value = float(qc_pixel_value)*qc_scale_factor
                ### Check
                if (qc_pixel_value >= qcf.getfloat('MXD09A1', 'sza_min')) is False:
                    self.invalid_pixels['sza_min'] += 1
                    pixel_pass_quality_control = False
                if (qc_pixel_value <= qcf.getfloat('MXD09A1', 'sza_max')) is False:
                    self.invalid_pixels['sza_max'] += 1
                    pixel_pass_quality_control = False

                return pixel_pass_quality_control

            #### View Zenith Angle Band ####
            def vza(qc_pixel_value):
                pixel_pass_quality_control = True
                # prepare data
                qc_scale_factor = 0.01
                qc_pixel_value = float(qc_pixel_value)*qc_scale_factor
                ### Check
                if (qc_pixel_value >= qcf.getfloat('MXD09A1', 'vza_min')) is False:
                    self.invalid_pixels['vza_min'] += 1
                    pixel_pass_quality_control = False
                if (qc_pixel_value <= qcf.getfloat('MXD09A1', 'vza_max')) is False:
                    self.invalid_pixels['vza_max'] += 1
                    pixel_pass_quality_control = False

                return pixel_pass_quality_control

            #### Relative Zenith Angle Band ####
            def rza(qc_pixel_value):
                pixel_pass_quality_control = True
                # prepare data
                qc_scale_factor = 0.01
                qc_pixel_value = float(qc_pixel_value)*qc_scale_factor
                ### Check
                if (qc_pixel_value >= qcf.getfloat('MXD09A1', 'rza_min')) is False:
                    self.invalid_pixels['rza_min'] += 1
                    pixel_pass_quality_control = False
                if (qc_pixel_value <= qcf.getfloat('MXD09A1', 'rza_max')) is False:
                    self.invalid_pixels['rza_max'] += 1
                    pixel_pass_quality_control = False

                return pixel_pass_quality_control

            #### Reflectance State QA Flags Band (sf) ####
            def sf(qc_pixel_value):
                pixel_pass_quality_control = True
                # prepare data
                qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), self.num_bits)
                ### Cloud State
                bits = qc_bin_str[0:2]
                if qcf.getboolean('MXD09A1', 'sf_cloud_state_'+bits) is False:
                    self.invalid_pixels['sf_cloud_state_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Cloud shadow
                qc_pixel_value = qc_bin_str[2]
                if (qcf.getboolean('MXD09A1', 'sf_cloud_shadow_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_cloud_shadow_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_cloud_shadow_1'):
                    self.invalid_pixels['sf_cloud_shadow_1'] += 1
                    pixel_pass_quality_control = False
                ### Land/Water flag
                bits = qc_bin_str[3:6]
                if qcf.getboolean('MXD09A1', 'sf_land_water_'+bits) is False:
                    self.invalid_pixels['sf_land_water_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Aerosol Quantity
                bits = qc_bin_str[6:8]
                if qcf.getboolean('MXD09A1', 'sf_aerosol_quantity_'+bits) is False:
                    self.invalid_pixels['sf_aerosol_quantity_'+bits] += 1
                    pixel_pass_quality_control = False
                ### cirrus_detected
                bits = qc_bin_str[8:10]
                if qcf.getboolean('MXD09A1', 'sf_cirrus_detected_'+bits) is False:
                    self.invalid_pixels['sf_cirrus_detected_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Internal Cloud Algorithm Flag
                qc_pixel_value = qc_bin_str[10]
                if (qcf.getboolean('MXD09A1', 'sf_internal_cloud_algorithm_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_internal_cloud_algorithm_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_internal_cloud_algorithm_1'):
                    self.invalid_pixels['sf_internal_cloud_algorithm_1'] += 1
                    pixel_pass_quality_control = False
                ### Internal Fire Algorithm Flag
                qc_pixel_value = qc_bin_str[11]
                if (qcf.getboolean('MXD09A1', 'sf_internal_fire_algorithm_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_internal_fire_algorithm_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_internal_fire_algorithm_1'):
                    self.invalid_pixels['sf_internal_fire_algorithm_1'] += 1
                    pixel_pass_quality_control = False
                ### MOD35 snow/ice flag
                qc_pixel_value = qc_bin_str[12]
                if (qcf.getboolean('MXD09A1', 'sf_mod35_snow_ice_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_mod35_snow_ice_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_mod35_snow_ice_1'):
                    self.invalid_pixels['sf_mod35_snow_ice_1'] += 1
                    pixel_pass_quality_control = False
                ### Pixel adjacent to cloud
                qc_pixel_value = qc_bin_str[13]
                if (qcf.getboolean('MXD09A1', 'sf_pixel_adjacent_to_cloud_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_pixel_adjacent_to_cloud_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_pixel_adjacent_to_cloud_1'):
                    self.invalid_pixels['sf_pixel_adjacent_to_cloud_1'] += 1
                    pixel_pass_quality_control = False
                ### Salt pan
                qc_pixel_value = qc_bin_str[14]
                if (qcf.getboolean('MXD09A1', 'sf_salt_pan_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_salt_pan_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_salt_pan_1'):
                    self.invalid_pixels['sf_salt_pan_1'] += 1
                    pixel_pass_quality_control = False
                ### Internal Snow Mask
                qc_pixel_value = qc_bin_str[15]
                if (qcf.getboolean('MXD09A1', 'sf_internal_snow_mask_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_internal_snow_mask_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09A1', 'sf_internal_snow_mask_1'):
                    self.invalid_pixels['sf_internal_snow_mask_1'] += 1
                    pixel_pass_quality_control = False

                return pixel_pass_quality_control

            # switch case for quality control band
            quality_control_band = {
                'rbq': rbq,
                'sza': sza,
                'vza': vza,
                'rza': rza,
                'sf': sf,
            }

            return quality_control_band[self.id_name](qc_pixel_value)

        # [MXD09Q1] ########################################################
        # for MOD09Q1 and MYD09Q1 (Collection 6)
        if self.sd_shortname in ['MOD09Q1', 'MYD09Q1']:

            #### Reflectance State QA Flags Band (sf) ####
            def sf(qc_pixel_value):
                pixel_pass_quality_control = True
                # prepare data
                qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), self.num_bits)
                ### Cloud State
                bits = qc_bin_str[0:2]
                if qcf.getboolean('MXD09Q1', 'sf_cloud_state_'+bits) is False:
                    self.invalid_pixels['sf_cloud_state_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Cloud shadow
                qc_pixel_value = qc_bin_str[2]
                if (qcf.getboolean('MXD09Q1', 'sf_cloud_shadow_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_cloud_shadow_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_cloud_shadow_1'):
                    self.invalid_pixels['sf_cloud_shadow_1'] += 1
                    pixel_pass_quality_control = False
                ### Land/Water flag
                bits = qc_bin_str[3:6]
                if qcf.getboolean('MXD09Q1', 'sf_land_water_'+bits) is False:
                    self.invalid_pixels['sf_land_water_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Aerosol Quantity
                bits = qc_bin_str[6:8]
                if qcf.getboolean('MXD09Q1', 'sf_aerosol_quantity_'+bits) is False:
                    self.invalid_pixels['sf_aerosol_quantity_'+bits] += 1
                    pixel_pass_quality_control = False
                ### cirrus_detected
                bits = qc_bin_str[8:10]
                if qcf.getboolean('MXD09Q1', 'sf_cirrus_detected_'+bits) is False:
                    self.invalid_pixels['sf_cirrus_detected_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Internal Cloud Algorithm Flag
                qc_pixel_value = qc_bin_str[10]
                if (qcf.getboolean('MXD09Q1', 'sf_internal_cloud_algorithm_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_internal_cloud_algorithm_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_internal_cloud_algorithm_1'):
                    self.invalid_pixels['sf_internal_cloud_algorithm_1'] += 1
                    pixel_pass_quality_control = False
                ### Internal Fire Algorithm Flag
                qc_pixel_value = qc_bin_str[11]
                if (qcf.getboolean('MXD09Q1', 'sf_internal_fire_algorithm_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_internal_fire_algorithm_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_internal_fire_algorithm_1'):
                    self.invalid_pixels['sf_internal_fire_algorithm_1'] += 1
                    pixel_pass_quality_control = False
                ### MOD35 snow/ice flag
                qc_pixel_value = qc_bin_str[12]
                if (qcf.getboolean('MXD09Q1', 'sf_mod35_snow_ice_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_mod35_snow_ice_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_mod35_snow_ice_1'):
                    self.invalid_pixels['sf_mod35_snow_ice_1'] += 1
                    pixel_pass_quality_control = False
                ### Pixel adjacent to cloud
                qc_pixel_value = qc_bin_str[13]
                if (qcf.getboolean('MXD09Q1', 'sf_pixel_adjacent_to_cloud_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_pixel_adjacent_to_cloud_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_pixel_adjacent_to_cloud_1'):
                    self.invalid_pixels['sf_pixel_adjacent_to_cloud_1'] += 1
                    pixel_pass_quality_control = False
                ### Salt pan
                qc_pixel_value = qc_bin_str[14]
                if (qcf.getboolean('MXD09Q1', 'sf_salt_pan_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_salt_pan_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_salt_pan_1'):
                    self.invalid_pixels['sf_salt_pan_1'] += 1
                    pixel_pass_quality_control = False
                ### Internal Snow Mask
                qc_pixel_value = qc_bin_str[15]
                if (qcf.getboolean('MXD09Q1', 'sf_internal_snow_mask_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['sf_internal_snow_mask_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'sf_internal_snow_mask_1'):
                    self.invalid_pixels['sf_internal_snow_mask_1'] += 1
                    pixel_pass_quality_control = False

                return pixel_pass_quality_control

            #### Reflectance Band Quality (rbq) ####
            def rbq(qc_pixel_value):
                pixel_pass_quality_control = True
                # prepare data
                qc_bin_str = fix_binary_string(int2bin(qc_pixel_value), self.num_bits)
                ### Modland QA
                bits = qc_bin_str[0:2]
                if qcf.getboolean('MXD09Q1', 'rbq_modland_qa_'+bits) is False:
                    self.invalid_pixels['rbq_modland_qa_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Data Quality
                bits = qc_bin_str[(band-1)*4+4:band*4+4]
                if qcf.getboolean('MXD09Q1', 'rbq_data_quality_'+bits) is False:
                    self.invalid_pixels['rbq_data_quality_'+bits] += 1
                    pixel_pass_quality_control = False
                ### Atmospheric correction
                qc_pixel_value = qc_bin_str[12]
                if (qcf.getboolean('MXD09Q1', 'rbq_atcorr_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['rbq_atcorr_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'rbq_atcorr_1'):
                    self.invalid_pixels['rbq_atcorr_1'] += 1
                    pixel_pass_quality_control = False
                ### Adjacency correction
                qc_pixel_value = qc_bin_str[13]
                if (qcf.getboolean('MXD09Q1', 'rbq_adjcorr_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['rbq_adjcorr_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'rbq_adjcorr_1'):
                    self.invalid_pixels['rbq_adjcorr_1'] += 1
                    pixel_pass_quality_control = False
                ### Different orbit
                qc_pixel_value = qc_bin_str[14]
                if (qcf.getboolean('MXD09Q1', 'rbq_difforbit_0') or bool(int(qc_pixel_value))) is False:
                    self.invalid_pixels['rbq_difforbit_0'] += 1
                    pixel_pass_quality_control = False
                if bool(int(qc_pixel_value)) and not qcf.getboolean('MXD09Q1', 'rbq_difforbit_1'):
                    self.invalid_pixels['rbq_difforbit_1'] += 1
                    pixel_pass_quality_control = False

                return pixel_pass_quality_control

            # switch case for quality control band
            quality_control_band = {
                'sf': sf,
                'rbq': rbq,
            }

            return quality_control_band[self.id_name](qc_pixel_value)
