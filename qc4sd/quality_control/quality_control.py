#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015-2016
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

import os
import gc
import osr
import resource
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from subprocess import call
from copy import deepcopy
from math import ceil, floor, isnan
try:
    from osgeo import gdal
except ImportError:
    import gdal

from qc4sd.lib import fix_zeros, chunks, merge_dicts, repulsive_items_list
from qc4sd.satellite_data.satellite_data import SatelliteData


class QualityControl:
    """Process the quality control for all input file for one
    band with the quality control settings based on quality control
    file.
    """
    # save all instances
    list = []

    def __init__(self, quality_control_file, band, with_stats):
        QualityControl.list.append(self)
        self.band = band
        self.band_name = 'band'+fix_zeros(band, 2)

        self.qcf = quality_control_file
        self.with_stats = with_stats

        self.qc_check_lists = {}

        self.output_driver = None
        self.output_bands = []
        self.output_filename = "{0}_{1}_band{2}.tif".format(SatelliteData.tile, SatelliteData.shortname, fix_zeros(band, 2))

        if self.with_stats:
            # for save some statistics fields after check the quality control
            self.quality_control_statistics = {}

            # initialize quality control bands class
            for sd in SatelliteData.list:
                for qc_id_name, qc_checker in sd.qc_bands.items():
                    qc_checker.init_statistics(quality_control_file)

    def __str__(self):
        return self.band_name

    def do_check_qc_by_chunk(self, x_chunk, sd):
        """Check the quality control for data band pixel per pixel
        processing it pixels grouped by chunks of rows in multiprocess
        """
        statistics = {'total_invalid_pixels': 0, 'nodata_pixels': 0, 'invalid_pixels': {}}

        #pixels_no_pass_qc = np.empty((0, 2), dtype=int)
        pixels_no_pass_qc = []

        for x in x_chunk:
            for y, data_band_pixel in enumerate(self.data_band_raster_to_process[x]):
                # for check a particular frame in the image, only for test
                # if not (0 < x < 200 and 200 < y < 400):
                #     continue

                # part 1 mode A
                #if not (968 < y < 1189 and 1361 < x < 1774):
                #    continue
                # part 2 mode A
                #if not (540 < y < 1041 and 2061 < x < 2367):
                #    continue
                # part 3 mode A
                #if not (745 < y < 1302 and 227 < x < 893):
                #    continue

                # part 1 mode Q
                # if not (1938 < y < 2378 and 2723 < x < 3549):
                #    continue
                # part 2 mode Q
                # if not (1082 < y < 2082 and 4124 < x < 4736):
                #    continue
                # part 3 mode Q
                #if not (1492 < y < 2604 and 456 < x < 1788):
                #    continue

                # GA 1000-1500  1800-2600
                #if not (1000 < y < 1700 and 600 < x < 1600):
                #   continue
                # GQ 1000-1500  1800-2600
                #if not (500 < y < 2800 and 2000 < x < 3000):
                #   continue

                # if pixel is not valid then don't check it and save statistic
                if data_band_pixel == int(self.nodata_value):
                    if self.with_stats:
                        statistics['nodata_pixels'] += 1
                        statistics['total_invalid_pixels'] += 1
                    continue

                # check pixel with all items of all quality control bands configured
                pixel_check_list = []
                for qc_id_name, qc_checker in sd.qc_bands.items():
                    qcc = qc_checker.quality_control_check(x, y, self.band, self.qcf, self.with_stats)
                    pixel_check_list.append(qcc)
                    if self.with_stats:
                        statistics['invalid_pixels'][qc_checker.full_name] = qc_checker.invalid_pixels
                    elif qcc is False:
                        break

                # the pixel pass or not pass the quality control:
                # check if all validate quality control for this pixel are True
                pixel_pass_quality_control = not (False in pixel_check_list)

                # if the pixel not pass the quality control, replace with NoData value
                if not pixel_pass_quality_control:
                    #pixels_no_pass_qc = np.append(pixels_no_pass_qc, [[x, y]], axis=0)
                    pixels_no_pass_qc.append([x, y])
                    if self.with_stats:
                        statistics['total_invalid_pixels'] += 1

        return statistics, pixels_no_pass_qc

    @staticmethod
    def calculate(func, args):
        statistics, pixels_no_pass_qc = func(*args)
        return statistics, pixels_no_pass_qc

    def meta_calculate(self, args):
        return self.calculate(*args)

    def process(self):
        """Process the quality control, this is check pixel per pixel
        for specific band to process for all input files. Save all
        raster 2d array checked (QC) sorted chronologically by date
        of input file.
        """
        # set unlimited to soft/hard memory for subprocess
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        resource.setrlimit(resource.RLIMIT_DATA, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

        number_of_processes = cpu_count() - 1
        if number_of_processes > 1:
            print('\n(Running with {0} local parallel processing)\n'.format(number_of_processes))

        # for each file
        for sd in SatelliteData.list:
            # statistics for this satellite data (pixels and quality controls bands)
            sd_statistics = {'total_pixels': sd.get_total_pixels(self.band), 'total_invalid_pixels': 0, 'nodata_pixels': 0, 'invalid_pixels': {}}
            # get NoData value specific for band/product
            self.nodata_value = sd.get_nodata_value(self.band)
            # get raster for band to process
            # TODO: optimize/performance the table open/access in memory (pytables?)
            self.data_band_raster_to_process = sd.get_data_band(self.band)

            # calculate the number of chunks
            n_chunks = ceil(sd.get_rows(self.band)/(number_of_processes*floor(sd.get_rows(self.band)/1000)))

            # divide the rows in n_chunks to process matrix in multiprocess (multi-rows)
            x_chunks = chunks(range(sd.get_rows(self.band)), n_chunks)

            try:
                print('Processing the image {0} in the band {1} ... '.format(sd.file_name, self.band), end="", flush=True)
                with ProcessPoolExecutor(max_workers=number_of_processes) as executor:
                    tasks = [(self.do_check_qc_by_chunk, (x_chunk, sd)) for x_chunk in x_chunks]
                    results = executor.map(self.meta_calculate, tasks)
                executor.shutdown()
            except Exception:
                print('\n   Problems processing this image in parallel, continue without '
                      'multiprocess ... ', end="", flush=True)
                results = [self.do_check_qc_by_chunk(range(0, sd.get_rows(self.band)), sd)]

            all_pixels_no_pass_qc = []
            for statistics, pixels_no_pass_qc in results:
                sd_statistics = merge_dicts(sd_statistics, statistics)
                all_pixels_no_pass_qc += pixels_no_pass_qc

            # save statistics
            if self.with_stats:
                self.quality_control_statistics[sd.start_year_and_jday] = sd_statistics

            # mask all pixels that no pass the quality control
            data_band_raster = sd.get_data_band(self.band)
            for x, y in all_pixels_no_pass_qc:
                data_band_raster[x, y] = self.nodata_value

            # save raster band for each input file with QC in sorted list chronologically
            self.output_bands.append(data_band_raster)

            # clean
            del self.data_band_raster_to_process, sd_statistics, data_band_raster, n_chunks, x_chunks, tasks, results
            # force run garbage collector memory
            gc.collect()

            print('done')

    def save_statistics(self, output_dir):
        """Save statistics of invalid pixels in a image that show the time series of
        all invalid pixels of all filters as the result after apply the QC4SD
        """
        # force matplotlib to not use any Xwindows backend.
        import matplotlib
        matplotlib.use('Agg')

        import matplotlib.ticker as mtick
        import matplotlib.pyplot as plt

        # path to save statistics
        path_stats = os.path.join(output_dir, self.output_filename.split('.tif')[0])
        # if not os.path.isdir(path_stats):
        #     os.makedirs(path_stats)

        ################################
        # graph invalid pixels for the time series

        img_filename = os.path.join(output_dir, self.output_filename.split('.tif')[0]+"_stats.png")
        print("Saving the image of statistics of invalid pixels in: {0}".format(os.path.basename(img_filename)))

        ################################
        # prepare data
        all_filter_names = set()
        for sd_invalid_pixels in self.quality_control_statistics.values():
            filters = sd_invalid_pixels['invalid_pixels']
            # delete elements if the values are empty
            filters = {k: filters[k] for k in filters if filters[k]}
            # unpacking the dicts of all filters
            filters = [x for x in filters.values()]
            _tmp_dict = {}
            for filter in filters:
                _tmp_dict.update(filter)
            filters = _tmp_dict
            all_filter_names = all_filter_names | set(filters.keys())
        all_filter_names = sorted(list(all_filter_names))

        sd_names_sorted = sorted(self.quality_control_statistics.keys())
        all_invalid_pixels = []
        for sd_name in sd_names_sorted:
            filters = self.quality_control_statistics[sd_name]['invalid_pixels']
            # delete elements if the values are empty
            filters = {k: filters[k] for k in filters if filters[k]}
            # unpacking the dicts of all filters
            filters = [x for x in filters.values()]
            _tmp_dict = {}
            for filter in filters:
                _tmp_dict.update(filter)
            filters = _tmp_dict

            sd_time_series = [self.quality_control_statistics[sd_name]['total_invalid_pixels']]
            sd_time_series += [self.quality_control_statistics[sd_name]['nodata_pixels']]
            for filter_name in all_filter_names:
                if filter_name in filters:
                    sd_time_series.append(filters[filter_name])
                else:
                    sd_time_series.append(float('nan'))
            all_invalid_pixels.append(sd_time_series)

        all_filter_names = ['total_invalid_pixels'] + ['nodata_pixels'] + list(all_filter_names)
        #all_filter_names = [name.replace('_', ' ') for name in all_filter_names]

        ################################
        # plot

        width = 10+len(sd_names_sorted)*0.4
        if len(sd_names_sorted) == 1: width = 7
        fig, ax = plt.subplots(1, 1, figsize=(width, 8), facecolor='white')
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        plt.tick_params(axis='both', which='both', bottom='off', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')
        all_invalid_pixels_T = list(map(list, zip(*all_invalid_pixels)))

        # delete all group of list that have only zeros, this is delete types of
        # invalid pixels that not filter any pixel in all image across the time
        delete_zeros_lists = [idx for idx, values in enumerate(all_invalid_pixels_T)
                              if [x for x in set(values) if not isnan(x)] == [0]]
        delete_zeros_lists.reverse()
        for del_idx in delete_zeros_lists:
                del all_invalid_pixels_T[del_idx]
                del all_filter_names[del_idx]
        # rewrite list after clean
        all_invalid_pixels = list(map(list, zip(*all_invalid_pixels_T)))

        if not all_invalid_pixels:
            print("\nWARNING: the invalid pixels is zero! nothing pixels was filtered.\n")
            return

        max_y = max([max(sub_l) for sub_l in all_invalid_pixels_T])  # y max over all times

        # fix position for y label
        y_pos_label_fixed = deepcopy(all_invalid_pixels[-1])
        # if any item in the last position is nan, put the last
        # valid value for this item
        for idx, y_pos in enumerate(y_pos_label_fixed):
            iter_pos = -1
            if isnan(y_pos):
                while isnan(all_invalid_pixels[iter_pos][idx]):
                    iter_pos += -1
                y_pos_label_fixed[idx] = all_invalid_pixels[iter_pos][idx]

        # set initial value for repulsive_items_list
        repulsive_distance = max_y * 0.035

        fix_list = True
        while fix_list:
            fix_list, repulsive_distance, y_pos_label_fixed = repulsive_items_list(y_pos_label_fixed, repulsive_distance)

        # define colors
        import matplotlib as mpl
        import matplotlib.cm as cm
        norm = mpl.colors.Normalize(vmin=0, vmax=len(all_invalid_pixels_T))
        cmap = cm.Set1
        m = cm.ScalarMappable(norm=norm, cmap=cmap)

        if len(sd_names_sorted) == 1:  # for only one image
            for idx, line in enumerate(all_invalid_pixels_T):
                if idx == 0:
                    plt.plot(0, line, 'ro', markersize=9, color=m.to_rgba(idx), linewidth=3.4, alpha=1)
                    # put value of total invalid pixel for each x item (time)
                    for x, y in zip(range(len(SatelliteData.list)), line):
                        ax.text(x, y+max_y*0.02, "{0}%".format(round(100*y/SatelliteData.list[idx].get_total_pixels(self.band), 2)),
                                ha='center', va='bottom', color=m.to_rgba(idx), fontweight='bold', fontsize=12, alpha=1)
                else:
                    plt.plot(0, line, 'ro', markersize=9, color=m.to_rgba(idx), linewidth=3, alpha=1)
                # y label of filter name
                plt.text(0.3, y_pos_label_fixed[idx], all_filter_names[idx],
                         fontsize=12, weight='bold', color=m.to_rgba(idx), alpha=1)
            plt.xlim(-0.5, 0.5)
            plt.xticks(range(len(sd_names_sorted)), sd_names_sorted, rotation=90)
            plt.ylim(-max_y*0.01, max_y+max_y*0.07)
            plt.title("Invalid pixels for {0} {1} in band {2}\nQC4SD - IDEAM".
                      format(SatelliteData.tile, SatelliteData.shortname, fix_zeros(self.band, 2)),
                      fontsize=18, weight='bold', color="#3A3A3A")
            plt.xlabel("Date", fontsize=14, weight='bold', color="#3A3A3A")
            plt.ylabel("Number of invalid pixels", fontsize=14, weight='bold', color="#3A3A3A")
            plt.tick_params(axis='both', which='major', labelsize=14, color="#3A3A3A")
            ax.grid(True, color='gray')
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%g'))
            fig.tight_layout()
            fig.subplots_adjust(right=0.6, left=0.4)
        else:
            for idx, line in enumerate(all_invalid_pixels_T):
                if idx == 0:
                    plt.plot(line, color=m.to_rgba(idx), linewidth=3.4, alpha=1)
                    # put value of total invalid pixel for each x item (time)
                    for x, y in zip(range(len(SatelliteData.list)), line):
                        ax.text(x, y+max_y*0.02, "{0}%".format(round(100*y/SatelliteData.list[idx].get_total_pixels(self.band), 2)),
                                ha='center', va='bottom', color=m.to_rgba(idx), fontweight='bold', fontsize=12, alpha=1)
                else:
                    plt.plot(line, color=m.to_rgba(idx), linewidth=3, alpha=1)
                # y label of filter name
                plt.text(len(SatelliteData.list)-1+len(SatelliteData.list)*0.02, y_pos_label_fixed[idx],
                         all_filter_names[idx], fontsize=12, weight='bold', color=m.to_rgba(idx), alpha=1)
            plt.xlim(-len(SatelliteData.list)*0.02, len(SatelliteData.list)-1+len(SatelliteData.list)*0.02)
            plt.xticks(range(len(sd_names_sorted)), sd_names_sorted, rotation=90)
            plt.ylim(-max_y*0.01, max_y+max_y*0.07)
            plt.title("Invalid pixels for {0} {1} in band {2}\nQC4SD - IDEAM".
                      format(SatelliteData.tile, SatelliteData.shortname, fix_zeros(self.band, 2)),
                      fontsize=18, weight='bold', color="#3A3A3A")
            plt.xlabel("Date", fontsize=14, weight='bold', color="#3A3A3A")
            plt.ylabel("Number of invalid pixels", fontsize=14, weight='bold', color="#3A3A3A")
            plt.tick_params(axis='both', which='major', labelsize=14, color="#3A3A3A")
            ax.grid(True, color='gray')
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%g'))
            fig.tight_layout()
            fig.subplots_adjust(right=1.02-3.6/width)

        plt.savefig(img_filename, dpi=86)
        plt.close('all')

        # trim whitespace
        try:
            call(["convert", img_filename, "-trim", "-bordercolor", "white", "-border", "8x8", "+repage", "-alpha", "off", img_filename])
            print('trim image successfully')
        except:
            pass

        # for sd_name, sd_invalid_pixels in self.quality_control_statistics.items():
        #     print()
        #     print(sd_name)
        #     print('total_invalid_pixels', sd_invalid_pixels['total_invalid_pixels'])
        #     for qc_id_name, qc_invalid_pixels in sd_invalid_pixels['invalid_pixels'].items():
        #         print('  '+qc_id_name)
        #         for qc_item, invalid in qc_invalid_pixels.items():
        #             if invalid != 0:
        #                 print('    ', qc_item+':', invalid)

    def save_results(self, output_dir):
        """Save all processed files in one file per each data band to process,
        each file to save has the precessed files as bands.

        :param output_dir: directory to save the output file
        :type output_dir: path
        """
        print("\nSaving the result for the band {0} in: {1}"
              .format(self.band, self.output_filename))
        # get gdal properties of one of data band
        sd = SatelliteData.list[0]
        data_band_name = [x for x in sd.sub_datasets if 'b'+fix_zeros(self.band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name, gdal.GA_ReadOnly)
        geotransform = gdal_data_band.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]

        # create output raster
        driver = gdal.GetDriverByName('GTiff')
        nbands = len(self.output_bands)
        outRaster = driver.Create(os.path.join(output_dir, self.output_filename),
                                  sd.get_cols(self.band), sd.get_rows(self.band),
                                  nbands, gdal.GDT_Int16, ["COMPRESS=LZW", "PREDICTOR=2", "TILED=YES"])

        # write bands
        for nband, data_band_raster in enumerate(self.output_bands):
            outband = outRaster.GetRasterBand(nband + 1)
            outband.WriteArray(data_band_raster)
            #outband.WriteArray(sd.get_data_band(self.band))
            outband.SetNoDataValue(self.nodata_value)
            #outband.FlushCache()  # FlushCache cause WriteEncodedTile/Strip() failed
            outband = None

        # set projection
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromWkt(gdal_data_band.GetProjectionRef())
        outRaster.SetProjection(outRasterSRS.ExportToWkt())

        gdal_data_band = None
        geotransform = None
        outRaster = None



