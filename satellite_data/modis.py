#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  (c) Copyright SMBYC - IDEAM 2015
#  Authors: Xavier Corredor Llano
#  Email: xcorredorl at ideam.gov.co

from osgeo import gdal
from datetime import datetime

from QC4SD.satellite_data.satellite_data import SatelliteData
from QC4SD.lib import fix_zeros
from QC4SD.quality_control.modis import ModisQC


class MODIS(SatelliteData):

    def __init__(self, file):
        """Initialize the class of MODIS products

        :param file: path to input file
        :type file: str
        """
        super().list.append(self)
        super().__init__(file)

        # load metadata
        self.satellite = self.metadata['ASSOCIATEDPLATFORMSHORTNAME']  # Terra
        self.shortname = self.metadata['SHORTNAME']  # MOD09A1
        self.longname = self.metadata['LONGNAME']  # MODIS/Terra Surface Reflectance 8-Day L3 Global 500m SIN Grid
        self.tile = self.metadata['LOCALGRANULEID'].split('.')[2]  # h10v07
        dt_d = [int(x) for x in self.metadata['PRODUCTIONDATETIME'].split('T')[0].split('-')]
        dt_h = [int(x) for x in self.metadata['PRODUCTIONDATETIME'].replace('.', ':').split('T')[1].split(':')[0:3]]
        self.datetime = datetime(dt_d[0], dt_d[1], dt_d[2], dt_h[0], dt_h[1], dt_h[2])

        # setup the quality control band to process with Gdal dataset.
        self.qc_name = [x for x in self.sub_datasets if '_qc_' in x[1]][0][0]
        #self.quality_control_band = gdal.Open(qc_name)
        #self.quality_control_raster = self.quality_control_band.ReadAsArray()

        #print(self.quality_control_band.ReadAsArray())

    def set_quality_control_bands(self):
        self.qc_bands = {}

        # for MOD09/MYD09 A1
        if self.shortname in ['MOD09A1', 'MYD09A1']:
            # define numbers of bits for the band value in binary

            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if '_qc_' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name, num_bits=32)
            # Solar Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'szen' in x[1]][0][0]
            self.qc_bands['sza'] = ModisQC(self.shortname, 'sza', qc_name)
            # View Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'vzen' in x[1]][0][0]
            self.qc_bands['vza'] = ModisQC(self.shortname, 'vza', qc_name)
            # Relative Zenith Angle
            qc_name = [x for x in self.sub_datasets if 'raz' in x[1]][0][0]
            self.qc_bands['rza'] = ModisQC(self.shortname, 'rza', qc_name)
            # State flags
            qc_name = [x for x in self.sub_datasets if '_state_' in x[1]][0][0]
            self.qc_bands['sf'] = ModisQC(self.shortname, 'sf', qc_name, num_bits=16)

        # for MOD09/MYD09 Q1
        if self.shortname in ['MOD09Q1', 'MYD09Q1']:
            # Reflectance band quality
            qc_name = [x for x in self.sub_datasets if '_qc_' in x[1]][0][0]
            self.qc_bands['rbq'] = ModisQC(self.shortname, 'rbq', qc_name)

    def get_data_band(self, band):
        """Return the raster of the data band for respective band
        of the file.

        :param band: band to process
        :type band: int
        :return: raster of the data band
        :rtype: ndarray
        """
        data_band_name = [x for x in self.sub_datasets if 'b'+fix_zeros(band, 2) in x[1]][0][0]
        gdal_data_band = gdal.Open(data_band_name(band))
        data_band_raster = gdal_data_band.ReadAsArray()
        return data_band_raster

    def get_quality_control_bands(self, band):


        return [x for x in self.sub_datasets if 'b0'+str(band) in x[1]][0][0]

    def is_quality_control_tile_approved(self):
        """Check if the general quality control values for the entire
        tile (based on metadata not qc band) are approved based on the
        quality control file.
        """

        # TODO
        return True

    def check_quality_control(self, pixel):
        """Check if the specific pixel in the tile pass the quality
        control, this is evaluate with the quality control value for
        the respective pixel position. The quality control evaluation
        based on the quality control file.
        """
        
        if not self.is_quality_control_tile_approved():
            return False



'''
HORIZONTALTILENUMBER 10
QUALITYCLASSPERCENTAGE500MBAND7 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0
VERSIONID 5
LOCALGRANULEID MOD09A1.A2014361.h10v07.005.2015006072800.hdf
CHARACTERISTICBINSIZE500M 463.312716527778
ASSOCIATEDINSTRUMENTSHORTNAME MODIS
AUTOMATICQUALITYFLAG Passed
PERCENTLANDSEAMASKCLASS 5, 7, 0, 0, 0, 0, 6, 83
NADIRDATARESOLUTION500M 500m
PERCENTPROCESSED 100
GRANULEBEGINNINGDATETIME 2014-12-27T15:25:00.000000Z, 2014-12-28T16:05:00.000000Z, 2014-12-29T15:10:00.000000Z, 2014-12-30T15:55:00.000000Z, 2014-12-31T15:00:00.000000Z, 2015-01-01T15:40:00.000000Z, 2015-01-02T14:50:00.000000Z, 2015-01-03T15:30:00.000000Z
QAPERCENTGOODQUALITY 86
PGEVERSION 5.0.11
PERCENTLOWSUN 0
AUTOMATICQUALITYFLAGEXPLANATION Always Passed
PRODUCTIONDATETIME 2015-01-06T07:28:00.000Z
ORBITNUMBER 80025
CHARACTERISTICBINANGULARSIZE250M 7.5
QAPERCENTNOTPRODUCEDOTHER 0
PERCENTCLOUDY 3
RESOLUTIONBANDS1AND2 500
GLOBALGRIDCOLUMNS500M 86400
SHORTNAME MOD09A1
QUALITYCLASSPERCENTAGE500MBAND1 61, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 39, 0, 0
QUALITYCLASSPERCENTAGE500MBAND3 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
QUALITYCLASSPERCENTAGE500MBAND2 59, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 41, 0, 0
QUALITYCLASSPERCENTAGE500MBAND5 83, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 12, 0, 0
QUALITYCLASSPERCENTAGE500MBAND4 99, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0
REPROCESSINGACTUAL reprocessed
QUALITYCLASSPERCENTAGE500MBAND6 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
NUMBEROFORBITS 12
RANGEBEGINNINGDATE 2014-12-27
RANGEENDINGDATE 2015-01-03
REPROCESSINGPLANNED further update is anticipated
EQUATORCROSSINGLONGITUDE -96.9617083060913
DATACOLUMNS250M 4800
RANGEENDINGTIME 23:59:59.000000
VERTICALTILENUMBER 7
QAPERCENTNOTPRODUCEDCLOUD 0
DAYNIGHTFLAG Day
EQUATORCROSSINGDATE 2015-01-03
GRINGPOINTLATITUDE 9.94787818114214, 19.9999999982039, 20.0209405716854, 9.96948730639416
GRANULEDAYOFYEAR 361, 362, 363, 364, 365, 1, 2, 3
ASSOCIATEDPLATFORMSHORTNAME Terra
PARAMETERNAME MOD09A1
GEOANYABNORMAL False
EQUATORCROSSINGTIME 17:10:29.863394
PROCESSINGCENTER MODAPS
SPSOPARAMETERS 2015
LOCALVERSIONID 5.0.11
SOUTHBOUNDINGCOORDINATE 9.99999999910196
SCIENCEQUALITYFLAGEXPLANATION See http://landweb.nascom.nasa.gov/cgi-bin/QA_WWW/qaFlagPage.cgi?sat=terra for the product Science Quality status.
PERCENTLAND 7
RANGEBEGINNINGTIME 00:00:00.000000
GRINGPOINTSEQUENCENO 1, 2, 3, 4
GEOESTMAXRMSERROR 50.0
DATACOLUMNS500M 2400
NORTHBOUNDINGCOORDINATE 19.9999999982039
GLOBALGRIDCOLUMNS250M 172800
EXCLUSIONGRINGFLAG N
EASTBOUNDINGCOORDINATE -71.0714009369909
GRINGPOINTLONGITUDE -81.2437612450365, -85.1342217894563, -74.1984376947788, -70.8090717387614
PERCENTSHADOW 6
QAPERCENTMISSINGDATA 0
GRANULEENDINGDATETIME 2014-12-27T17:05:00.000000Z, 2014-12-28T16:15:00.000000Z, 2014-12-29T16:55:00.000000Z, 2014-12-30T16:00:00.000000Z, 2014-12-31T16:45:00.000000Z, 2015-01-01T15:50:00.000000Z, 2015-01-02T16:35:00.000000Z, 2015-01-03T15:40:00.000000Z
QAPERCENTINTERPOLATEDDATA 0
WESTBOUNDINGCOORDINATE -85.1342217894563
QAPERCENTOUTOFBOUNDSDATA 0
PROCESSVERSION 5.0.11
DATAROWS500M 2400
CHARACTERISTICBINANGULARSIZE500M 15.0
PROCESSINGENVIRONMENT Linux minion5064 2.6.18-371.3.1.el5PAE #1 SMP Thu Dec 5 13:29:20 EST 2013 i686 i686 i386 GNU/Linux
LONGNAME MODIS/Terra Surface Reflectance 8-Day L3 Global 500m SIN Grid
GLOBALGRIDROWS250M 86400
HDFEOSVersion HDFEOS_V2.9
GRANULEDAYNIGHTFLAG Day, Day, Day, Day, Day, Day, Day, Day
SYSTEMFILENAME MOD09GQ.A2014361.h10v07.005.2014363062301.hdf, MOD09GQ.A2014362.h10v07.005.2014364063859.hdf, MOD09GQ.A2014363.h10v07.005.2015001052406.hdf, MOD09GQ.A2014364.h10v07.005.2015001074052.hdf, MOD09GQ.A2014365.h10v07.005.2015005235759.hdf, MOD09GQ.A2015001.h10v07.005.2015006003000.hdf, MOD09GQ.A2015002.h10v07.005.2015004063445.hdf, MOD09GQ.A2015003.h10v07.005.2015006063429.hdf, MOD09GA.A2014361.h10v07.005.2014363062300.hdf, MOD09GA.A2014362.h10v07.005.2014364063859.hdf, MOD09GA.A2014363.h10v07.005.2015001052405.hdf, MOD09GA.A2014364.h10v07.005.2015001074052.hdf, MOD09GA.A2014365.h10v07.005.2015005235758.hdf, MOD09GA.A2015001.h10v07.005.2015006003000.hdf, MOD09GA.A2015002.h10v07.005.2015004063445.hdf, MOD09GA.A2015003.h10v07.005.2015006063429.hdf
TileID 51010007
DATAROWS250M 4800
ASSOCIATEDSENSORSHORTNAME MODIS
SCIENCEQUALITYFLAG Not Investigated
INPUTPOINTER MOD09GQ.A2014361.h10v07.005.2014363062301.hdf, MOD09GQ.A2014362.h10v07.005.2014364063859.hdf, MOD09GQ.A2014363.h10v07.005.2015001052406.hdf, MOD09GQ.A2014364.h10v07.005.2015001074052.hdf, MOD09GQ.A2014365.h10v07.005.2015005235759.hdf, MOD09GQ.A2015001.h10v07.005.2015006003000.hdf, MOD09GQ.A2015002.h10v07.005.2015004063445.hdf, MOD09GQ.A2015003.h10v07.005.2015006063429.hdf, MOD09GA.A2014361.h10v07.005.2014363062300.hdf, MOD09GA.A2014362.h10v07.005.2014364063859.hdf, MOD09GA.A2014363.h10v07.005.2015001052405.hdf, MOD09GA.A2014364.h10v07.005.2015001074052.hdf, MOD09GA.A2014365.h10v07.005.2015005235758.hdf, MOD09GA.A2015001.h10v07.005.2015006003000.hdf, MOD09GA.A2015002.h10v07.005.2015004063445.hdf, MOD09GA.A2015003.h10v07.005.2015006063429.hdf
CHARACTERISTICBINSIZE250M 231.656358263889
QAPERCENTPOOROUTPUT500MBAND2 41
NUMBEROFGRANULES 8
GLOBALGRIDROWS500M 43200
DESCRREVISION 5.1
QAPERCENTPOOROUTPUT500MBAND7 1
QAPERCENTPOOROUTPUT500MBAND6 0
QAPERCENTPOOROUTPUT500MBAND5 12
QAPERCENTPOOROUTPUT500MBAND4 1
QAPERCENTPOOROUTPUT500MBAND3 0
QAPERCENTOTHERQUALITY 13
QAPERCENTPOOROUTPUT500MBAND1 39
NADIRDATARESOLUTION250M 250m
'''