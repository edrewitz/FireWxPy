# THIS SCRIPT HAS FUNCTIONS THAT DOWNLOAD FORECAST DATA FROM THE NOAA/NWS FTP SERVER, ORGANIZE THE GRIB FILES AND RETURN BOOLEAN VALUES DEPENDING ON IF THE GRIB FILE EXISTS OR NOT
#
# THIS IS THE NWS FTP DATA ACCESS FILE FOR FIREPY
#
# THIS SCRIPT ALSO ACCESSES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATA (RTMA DATA) FROM THE UCAR THREDDS SERVER. RTMA DATA IS USEFUL FOR REAL-TIME ANALYSIS PLOTTING
#
#
# DEPENDENCIES INCLUDE:
# 1. PYGRIB
# 2. XARRAY
# 3. OS
# 4. FTPLIB
# 5. DATETIME
# 6. SIPHON
# 7. METPY
#
#  (C) METEOROLOGIST ERIC J. DREWITZ
#               USDA/USFS

##### IMPORTS NEEDED PYTHON MODULES #######
import pygrib
import xarray as xr
import os
import metpy
import metpy.calc as mpcalc
import parsers
import pandas as pd
import cartopy.crs as ccrs

from ftplib import FTP
from datetime import datetime, timedelta
from siphon.catalog import TDSCatalog
from metpy.cbook import get_test_data
from io import StringIO
from metpy.io import parse_metar_file
from metpy.units import units, pandas_dataframe_to_unit_arrays

class info:

    r'''

    THIS CLASS HOSTS FUNCTIONS THAT DISPLAY ERROR MESSAGES TO THE USER FOR A VARIETY OF TYPES OF USER ERROR

    (C) METEOROLOGIST ERIC J. DREWITZ 2023

    '''

    def directory_name_error():
        error_msg = f"""
    
        WARNING: USER ENTERED AN INVALID DIRECTORY NAME
    
        HERE IS THE URL FOR THE NOAA/NWS FTP SERVER WEBSITE: https://tgftp.nws.noaa.gov/
    
        HERE IS THE LIST OF VALID DIRECTORY NAMES ***NOTE USER STILL NEEDS TO ENTER THE LAST PORTION OF THE DIRECTORY NAME***
        
        AN EXAMPLE OF THE LAST PORTION OF A DIRECTORY NAME IS AS FOLLOWS: /VP.001-003/
    
        FULL DIRECTORY NAME LIST:
    
        ALASKA: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.alaska/
        CONUS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/
        CENTRAL GREAT LAKES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crgrlake/
        CENTRAL MISSISSIPPI VALLEY: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crmissvy/
        CENTRAL PLAINS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crplains/
        CENTRAL ROCKIES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crrocks/
        EASTERN GREAT LAKES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.ergrlake/
        GUAM: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.guam/
        HAWAII: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.hawaii/
        MID-ATLANTIC: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.midatlan/
        NORTHEAST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.neast/
        NORTHERN HEMISPHERE: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nhemi/
        NORTH PACIFIC OCEAN: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.npacocn/
        NORTHERN PLAINS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nplains/
        NORTHERN ROCKIES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nrockies/
        OCEANIC: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.oceanic/
        PACIFIC NORTHWEST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacnwest/
        PACIFIC SOUTHWEST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/
        PUERTO RICO: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.puertori/
        SOUTHEAST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.seast/
        SOUTHERN MISSISSIPPI VALLEY: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.smissvly/
        SOUTHERN PLAINS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.splains/
        SOUTHERN ROCKIES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.srockies/
        UPPER MISSISSIPPI VALLEY: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.umissvly/
        
        """
        print(error_msg)
    
    def directory_list():
        dir_list = f"""
        
        FULL DIRECTORY NAME LIST:
            
        ALASKA: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.alaska/
        CONUS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/
        CENTRAL GREAT LAKES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crgrlake/
        CENTRAL MISSISSIPPI VALLEY: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crmissvy/
        CENTRAL PLAINS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crplains/
        CENTRAL ROCKIES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crrocks/
        EASTERN GREAT LAKES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.ergrlake/
        GUAM: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.guam/
        HAWAII: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.hawaii/
        MID-ATLANTIC: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.midatlan/
        NORTHEAST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.neast/
        NORTHERN HEMISPHERE: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nhemi/
        NORTH PACIFIC OCEAN: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.npacocn/
        NORTHERN PLAINS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nplains/
        NORTHERN ROCKIES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nrockies/
        OCEANIC: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.oceanic/
        PACIFIC NORTHWEST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacnwest/
        PACIFIC SOUTHWEST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/
        PUERTO RICO: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.puertori/
        SOUTHEAST: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.seast/
        SOUTHERN MISSISSIPPI VALLEY: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.smissvly/
        SOUTHERN PLAINS: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.splains/
        SOUTHERN ROCKIES: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.srockies/
        UPPER MISSISSIPPI VALLEY: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.umissvly/
        
        """
        print(dir_list)
    
    
    def parameter_name_error():
        error_msg = f"""
    
        WARNING: USER ENTERED AN INVALID PARAMETER NAME. 
    
        FOR THE FULL LIST OF PARAMETER NAMES VISIT THE FOLLOWING LINK:
    
        https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fwww.weather.gov%2Fmedia%2Fmdl%2Fndfd%2FNDFDelem_fullres.xls&wdOrigin=BROWSELINK
    
        """
        print(error_msg)
    
    
    def parameter_list():
        param_list = f"""
    
        FOR THE FULL LIST OF PARAMETERS, PLEASE VISIT THE FOLLOWING LINK:
    
        https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fwww.weather.gov%2Fmedia%2Fmdl%2Fndfd%2FNDFDelem_fullres.xls&wdOrigin=BROWSELINK
    
        """
        print(param_list)
    
    def invalid_element():
        error_msg = f"""
    
        WARNING: USER ENTERED INVALID SYNTAX FOR THE FORECAST PARAMETER.
    
        VISIT THIS LINK FOR THE FULL LIST OF ALL FORECAST PARAMETERS IN THE PROPER SYNTAX
    
        https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/NDFD/NWS/CONUS/CONDUIT/Best.html
    
        """
        print(error_msg)

    def syntax_error():
        error_msg = f"""
    
        WARNING: DATA COULD NOT BE RETRIEVED. 
    
        THIS IS DUE TO A LIKELY SYNTAX ERROR. 
    
        THIS IS MOST LIKELY DUE TO THE PARAMETER BEING DEFINED WITH INCORRECT SYNTAX
    
        FOR THE FULL OPENDAP LIST OF PARAMETERS FOR REAL TIME MESOSCALE ANALYSIS DATA VISIT
    
        https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/RTMA/CONUS_2p5km/Best.html
    
        """
    
        print(error_msg)


    def invalid_parameter_NOMADS_RTMA_Alaska():
        error_msg = f"""

        WARNING: USER ENTERED AN INVALID PARAMETER NAME

        HERE IS THE LIST OF VALID PARAMETER NAMES FOR ALASKA RTMA DATA

        Variables:
            (total of 13)
             
            ceilceil
            ** cloud ceiling ceiling [m]
             
            dpt2m
            ** 2 m above ground dew point temperature [k]
             
            gust10m
            ** 10 m above ground wind speed (gust) [m/s]
             
            hgtsfc
            ** surface geopotential height [gpm]
             
            pressfc
            ** surface pressure [pa]
             
            spfh2m
            ** 2 m above ground specific humidity [kg/kg]
             
            tcdcclm
            ** entire atmosphere (considered as a single layer) total cloud cover [%]
             
            tmp2m
            ** 2 m above ground temperature [k]
             
            ugrd10m
            ** 10 m above ground u-component of wind [m/s]
             
            vgrd10m
            ** 10 m above ground v-component of wind [m/s]
             
            vissfc
            ** surface visibility [m]
             
            wdir10m
            ** 10 m above ground wind direction (from which blowing) [degtrue]
             
            wind10m
            ** 10 m above ground wind speed [m/s]

        """
        print(error_msg)


class FTP_Downloads:

    r'''

    THIS CLASS HOSTS FUNCTIONS THAT USE THE FTPLIB MODULE TO PING AND DOWNLOAD WEATHER DATA FROM FTP SERVERS

    (C) METEOROLOGIST ERIC J. DREWITZ 2023

    '''

    def get_NWS_NDFD_short_term_grid_data(directory_name, parameter):
        
        r'''
        THIS FUNCTION DOWNLOADS THE DAYS 1-3 FORECAST DATA FROM THE NOAA/NWS FTP SERVER. 
    
        THE USER NEEDS TO ENTER THE NAME OF THE DIRECTORY IN WHICH THE USER NEEDS DATA FROM AS WELL AS THE PARAMETER
    
        FOR THE FULL LIST OF THE VARIOUS PARAMETERS PLEASE REFER TO: 
    
        https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fwww.weather.gov%2Fmedia%2Fmdl%2Fndfd%2FNDFDelem_fullres.xls&wdOrigin=BROWSELINK
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
    
        ###################################################
        # NDFD GRIDS DATA ACCESS FROM NOAA/NWS FTP SERVER #
        ###################################################
    
        ### CONNECTS TO THE NOAA/NWS FTP SERVER ###
        ftp = FTP('tgftp.nws.noaa.gov')
        ftp.login()
    
        ### SEARCHES FOR THE CORRECT DIRECTORY ###
        try:
            dirName = directory_name + 'VP.001-003/'
            param = parameter
            files = ftp.cwd(dirName)
    
            ### SEARCHES FOR THE CORRECT PARAMETER ###
            try:
                ################################
                # DOWNLOADS THE NWS NDFD GRIDS #
                ################################
                
                with open(param, 'wb') as fp:
                    ftp.retrbinary('RETR ' + param, fp.write)    
                
                ftp.close()
                
                #########################
                # DATA ARRAYS PARAMETER #
                #########################
                
                ds = xr.load_dataset(param, engine='cfgrib')
                grbs = pygrib.open(param)
                grbs.seek(0)
                return grbs
    
            ### ERROR MESSAGE WHEN THERE IS AN INVALID PARAMETER NAME ###
    
            except Exception as a:
                param_error = info.parameter_name_error()
                return param_error
    
        ### ERROR MESSAGE WHEN THERE IS AN INVALID DIRECTORY NAME ###
            
        except Exception as e:
            dir_error = info.directory_name_error()
            return dir_error
    
    
    def get_NWS_NDFD_extended_grid_data(directory_name, parameter):
        
        r'''
        THIS FUNCTION DOWNLOADS THE DAYS 4-7 FORECAST DATA FROM THE NOAA/NWS FTP SERVER. 
    
        THE USER NEEDS TO ENTER THE NAME OF THE DIRECTORY IN WHICH THE USER NEEDS DATA FROM AS WELL AS THE PARAMETER
    
        FOR THE FULL LIST OF THE VARIOUS PARAMETERS PLEASE REFER TO: 
    
        https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fwww.weather.gov%2Fmedia%2Fmdl%2Fndfd%2FNDFDelem_fullres.xls&wdOrigin=BROWSELINK
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
    
        ###################################################
        # NDFD GRIDS DATA ACCESS FROM NOAA/NWS FTP SERVER #
        ###################################################
    
        ### CONNECTS TO THE NOAA/NWS FTP SERVER ###
        ftp = FTP('tgftp.nws.noaa.gov')
        ftp.login()
    
        ### SEARCHES FOR THE CORRECT DIRECTORY ###
        try:
            dirName = directory_name + 'VP.004-007/'
            param = parameter
            files = ftp.cwd(dirName)
    
            ### SEARCHES FOR THE CORRECT PARAMETER ###
            try:
                ################################
                # DOWNLOADS THE NWS NDFD GRIDS #
                ################################
                
                with open(param, 'wb') as fp:
                    ftp.retrbinary('RETR ' + param, fp.write)    
                
                ftp.close()
                
                #########################
                # DATA ARRAYS PARAMETER #
                #########################
                
                ds = xr.load_dataset(param, engine='cfgrib')
                grbs = pygrib.open(param)
                grbs.seek(0)
                return grbs
    
            ### ERROR MESSAGE WHEN THERE IS AN INVALID PARAMETER NAME ###
    
            except Exception as a:
                param_error = info.parameter_name_error()
                return param_error
    
        ### ERROR MESSAGE WHEN THERE IS AN INVALID DIRECTORY NAME ###
            
        except Exception as e:
            dir_error = info.directory_name_error()
            return dir_error

    def get_first_half_of_data(directory_name, parameter):

        r'''
        THIS FUNCTION DOWNLOADS THE NATIONAL WEATHER SERVICE FORECAST DATA AND PARSES THROUGH THE DATA TO EXTRACT ALL THE VALUES. THIS IS NEEDED TO BE DONE SINCE THE NATIONAL WEATHER SERVICE KEEPS THEIR SHORT-TERM AND EXTENDED FORECAST DATA SEPERATE ON THEIR FTP SERVER. WE NEED TO EXTRACT THE VALUES FOR THE SHORT-TERM DATA IN A SEPERATE FUNCTION SINCE WHEN PREVIOUSLY TESTING THE DATA KEPT OVERWRITNG ITSELF DUE TO THE FILENAMES BEING THE SAME DESPITE THE DATA IS FOR DIFFERENT FORECAST PERIODS. 

        (C) METEOROLOGIST ERIC J. DREWITZ 2023

        '''
        
        short_term_data = FTP_Downloads.get_NWS_NDFD_short_term_grid_data(directory_name, parameter)
        first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files = parsers.NDFD.sort_GRIB_files(short_term_data, parameter)
        grid_time_interval = 12  
        
        grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5 = parsers.NDFD.parse_GRIB_files(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files, grid_time_interval, parameter)
    
        return grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5

    def get_full_7_day_grid_data(directory_name, parameter):

        r'''
        THIS FUNCTION USES THE PREVIOUS FUNCTION TO EXTRACT THE SHORT-TERM NATIONAL WEATHER SERVICE FORECAST DATA BEFORE DOWNLOADING AND EXTRACTING THE NATIONAL WEATHER SERVICE FORECAST DATA FOR THE EXTENDED PERIOD. THIS FUNCTION THEN RETURNS ALL 7 DAYS WORTH OF NATIONAL WEATHER SERVICE FORECAST DATA. 

        (C) METEOROLOGIST ERIC J. DREWITZ 2023

        '''
        
        grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5 = FTP_Downloads.get_first_half_of_data(directory_name, parameter)
        extended_data = FTP_Downloads.get_NWS_NDFD_extended_grid_data(directory_name, parameter)
        first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files = parsers.NDFD.sort_GRIB_files(extended_data, parameter)
        grid_time_interval = 12  
        
        grb_6_vals, grb_6_start, grb_6_end, grb_7_vals, grb_7_start, grb_7_end, grb_8_vals, grb_8_start, grb_8_end, grb_9_vals, grb_9_start, grb_9_end, grb_10_vals, grb_10_start, grb_10_end, lats_6, lons_6, lats_7, lons_7, lats_8, lons_8, lats_9, lons_9, lats_10, lons_10 = parsers.NDFD.parse_GRIB_files(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files, grid_time_interval, parameter)
    
        return grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5, grb_6_vals, grb_6_start, grb_6_end, grb_7_vals, grb_7_start, grb_7_end, grb_8_vals, grb_8_start, grb_8_end, grb_9_vals, grb_9_start, grb_9_end, grb_10_vals, grb_10_start, grb_10_end, lats_6, lons_6, lats_7, lons_7, lats_8, lons_8, lats_9, lons_9, lats_10, lons_10 
        

class UCAR_THREDDS_SERVER_OPENDAP_Downloads:

    r'''

    THIS CLASS HOSTS FUNCTIONS TO DOWNLOAD VARIOUS TYPES OF DATASETS FROM THE UCAR THREDDS SERVER

    (C) METEOROLOGIST ERIC J. DREWITZ 2023


    '''    

    class CONUS:
    
    
        def get_current_rtma_data(current_time, parameter):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASET FOR A PARAMETER SPECIFIED BY THE USER
        
            IF THE DATASET FOR THE CURRENT TIME IS UNAVAILABLE THE FUNCTION WILL TRY TO RETURN THE MOST RECENT DATASET IN THE PAST 4 HOURS
        
            IF THE USER HAS A SYNTAX ERROR THE LINK TO THE UCAR THREDDS OPENDAP PARAMETER LIST WILL BE DISPLAYED
        
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            CURRENT RTMA DATASET FOR THE PARAMETER DEFINED BY THE USER
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
        
            for i in range(1,5):
                new_time = current_time - timedelta(hours=i)
                times.append(new_time)
        
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+current_time.strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+current_time.strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_parameter = rtma_data[parameter].squeeze()

                print("Data retrieval for " + current_time.strftime('%m/%d/%Y %H00 UTC') + " is successful")
                
                return rtma_parameter, current_time
                
            except Exception as e:
        
                print(parameter + " Data is unavailiable for "+current_time.strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[0].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_parameter = rtma_data[parameter].squeeze()
                    time = times[0]
        
                    print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")
                    return rtma_parameter, time
        
                except Exception as a:
        
                    print(parameter + " Data is unavailiable for "+times[0].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[1].strftime('%m/%d/%Y %H00 UTC'))
                   
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_parameter = rtma_data[parameter].squeeze()
                        time = times[1]
            
                        print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")
                        return rtma_parameter, time
        
        
                    except Exception as b:
                                    
                        print(parameter + " Data is unavailiable for "+times[1].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[2].strftime('%m/%d/%Y %H00 UTC'))
        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_parameter = rtma_data[parameter].squeeze()
                            time = times[2]
            
                            print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")
                            return rtma_parameter, time
        
                        except Exception as c:
                                    
                            print(parameter + " Data is unavailiable for "+times[3].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[3].strftime('%m/%d/%Y %H00 UTC'))
        
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_parameter = rtma_data[parameter].squeeze()
                                time = times[3]
                
                                print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")
                                return rtma_parameter, time
                            
                        
                            except syntaxError as k:
                                error = info.syntax_error()
        
                                return error
        
        
        def get_rtma_data_24_hour_difference(current_time, parameter):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASET FOR A PARAMETER SPECIFIED BY THE USER
        
            THIS FUNCTION ALSO RETRIEVES THE DATASET FROM 24 HOURS PRIOR TO THE CURRENT DATASET FOR A 24 HOUR COMPARISON
        
            THE 24 HOUR COMPARISON IS SUBTRACTING THE CURRENT VALUES FROM THE VALUES FROM 24 HOURS AGO TO SHOW THE CHANGE
            
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            THE DIFFERENCE IN VALUES BETWEEN THE CURRENT DATASET AND DATASET FROM 24 HOURS AGO FOR THE PARAMETER DEFINED BY THE USER
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
            times_24 = []
        
            for i in range(0,5):
                new_time = current_time - timedelta(hours=i)
                old_time = new_time - timedelta(hours=24)
                times.append(new_time)
                times_24.append(old_time)
                
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_parameter = rtma_data[parameter].squeeze()
        
                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                rtma_parameter_24 = rtma_data_24[parameter].squeeze()
        
                print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                time = times[0]
                
                return rtma_parameter - rtma_parameter_24, time
                
            except Exception as e:
                
                print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[0].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                print("Will try to download the most recent datasets from "+times[1].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[1].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_parameter = rtma_data[parameter].squeeze()
            
                    rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data_24 = rtma_data_24.metpy.parse_cf()
                    rtma_parameter_24 = rtma_data_24[parameter].squeeze()
            
                    print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                    time = times[1]
                    
                    return rtma_parameter - rtma_parameter_24, time
             
                except Exception as a:
        
                    print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[1].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                    print("Will try to download the most recent datasets from "+times[2].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[2].strftime('%m/%d/%Y %H00 UTC'))
                    
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_parameter = rtma_data[parameter].squeeze()
                
                        rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data_24 = rtma_data_24.metpy.parse_cf()
                        rtma_parameter_24 = rtma_data_24[parameter].squeeze()
                
                        print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                        time = times[2]
                        
                        return rtma_parameter - rtma_parameter_24, time
        
        
                    except Exception as b:
                                    
                        print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[2].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                        print("Will try to download the most recent datasets from "+times[3].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[3].strftime('%m/%d/%Y %H00 UTC'))
                        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_parameter = rtma_data[parameter].squeeze()
                    
                            rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data_24 = rtma_data_24.metpy.parse_cf()
                            rtma_parameter_24 = rtma_data_24[parameter].squeeze()
                    
                            print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                            time = times[3]
                            
                            return rtma_parameter - rtma_parameter_24, time
        
                        except Exception as c:
                                    
                            print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[3].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                            print("Will try to download the most recent datasets from "+times[4].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[4].strftime('%m/%d/%Y %H00 UTC'))
                            
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_parameter = rtma_data[parameter].squeeze()
                        
                                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                                rtma_parameter_24 = rtma_data_24[parameter].squeeze()
                        
                                print("Data retrieval for " + times[4].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[4].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                                time = times[4]
                                
                                return rtma_parameter - rtma_parameter_24, time
                                      
                        
                            except syntaxError as k:
                                error = info.syntax_error()
        
                                return error
        
        
        def get_current_rtma_relative_humidity_data(current_time):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASETS FOR TEMPERATURE AND DEWPOINT
        
            THIS FUNCTION THEN CALCULATES A RELATIVE HUMIDITY DATASET USING METPY.CALC FROM THE TEMPERATURE AND DEWPOINT DATASETS
        
            IF THE DATASET FOR THE CURRENT TIME IS UNAVAILABLE THE FUNCTION WILL TRY TO RETURN THE MOST RECENT DATASET IN THE PAST 4 HOURS
        
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            CURRENT RTMA DATASET FOR RELATIVE HUMIDITY
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
        
            for i in range(0,5):
                new_time = current_time - timedelta(hours=i)
                times.append(new_time)
        
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
        
                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                time = times[0]
                
                return rtma_rh *100, time
                
            except Exception as e:
        
                print("Relative Humidity Data is unavailiable for "+times[0].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[1].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                    rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
            
                    rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                    print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                    time = times[1]
                    
                    return rtma_rh *100, time
          
                except Exception as a:
        
                    print("Relative Humidity data is unavailiable for "+times[1].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[2].strftime('%m/%d/%Y %H00 UTC'))
                    
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                        rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                
                        rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                        print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                        time = times[2]
                        
                        return rtma_rh *100, time
        
                    except Exception as b:
                                    
                        print("Relative Humidity data is unavailiable for "+times[2].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[3].strftime('%m/%d/%Y %H00 UTC'))
                        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                            rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                    
                            rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                            print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                            time = times[3]
                            
                            return rtma_rh *100, time
        
                        except Exception as c:
                                    
                            print("Relative Humidity data is unavailiable for "+times[3].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[4].strftime('%m/%d/%Y %H00 UTC'))
                            
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                        
                                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                                print("Data retrieval for " + times[4].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                                time = times[4]
                                
                                return rtma_rh *100, time
                                       
                        
                            except Exception as k:
                                print("WARNING: Latest dataset is more than 4 hours old.\nQuitting - Please try again later.")
        
                                return None
        
        
        def get_rtma_relative_humidity_24_hour_difference_data(current_time):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASETS FOR TEMPERATURE AND DEWPOINT AND THE CORRESPONDING DATASETS FROM 24 HOURS AGO
        
            THIS FUNCTION THEN CALCULATES A RELATIVE HUMIDITY DATASET USING METPY.CALC FROM THE TEMPERATURE AND DEWPOINT DATASETS
        
            IF THE DATASET FOR THE CURRENT TIME IS UNAVAILABLE THE FUNCTION WILL SEARCH FOR THE LATEST DATASET IN THE PAST 4 HOURS
        
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            24 HOUR DIFFERENCE IN RELATIVE HUMIDITY
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
            times_24 = []
        
            for i in range(0,5):
                new_time = current_time - timedelta(hours=i)
                old_time = new_time - timedelta(hours=24)
                times.append(new_time)
                times_24.append(old_time)
        
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
        
                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
        
                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
        
                rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                print("Data retrieval for both " + times[0].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                time = times[0]
                
                return (rtma_rh - rtma_rh_24) *100, time
                
            except Exception as e:
        
                print("Relative Humidity Data is unavailiable for "+times[0].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[0].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[1].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[1].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                    rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
            
                    rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
            
                    rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data_24 = rtma_data_24.metpy.parse_cf()
                    rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                    rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
            
                    rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                    print("Data retrieval for both " + times[1].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                    time = times[1]
                    
                    return (rtma_rh - rtma_rh_24) *100, time 
                    
                except Exception as a:
        
                    print("Relative Humidity Data is unavailiable for "+times[1].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[1].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[2].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[2].strftime('%m/%d/%Y %H00 UTC'))
                    
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                        rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                
                        rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                
                        rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data_24 = rtma_data_24.metpy.parse_cf()
                        rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                        rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                
                        rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                        print("Data retrieval for both " + times[2].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")
                        
                        time = times[2]
                        return (rtma_rh - rtma_rh_24) *100, time 
                        
                    except Exception as b:
                                    
                        print("Relative Humidity Data is unavailiable for "+times[2].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[2].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[3].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[3].strftime('%m/%d/%Y %H00 UTC'))
                        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                            rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                    
                            rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                    
                            rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data_24 = rtma_data_24.metpy.parse_cf()
                            rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                            rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                    
                            rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                            print("Data retrieval for both " + times[3].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                            time = times[3]
                            
                            return (rtma_rh - rtma_rh_24) *100, time 
         
                        except Exception as c:
                                    
                            print("Relative Humidity Data is unavailiable for "+times[3].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[3].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[4].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[4].strftime('%m/%d/%Y %H00 UTC'))
                    
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_CONUS_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                        
                                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                        
                                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/RTMA_CONUS_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data_24 = rtma_cat_24.datasets['RTMA_CONUS_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                                rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                                rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                        
                                rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                                print("Data retrieval for both " + times[4].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[4].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                                time = times[4]
                                
                                return (rtma_rh - rtma_rh_24) *100, time 
                
                            except Exception as k:
                                print("WARNING: Latest dataset is more than 4 hours old.\nQuitting - Please try again later.")
        
                                return None


    class GUAM:

        r'''
        THIS CLASS HAS FUNCTIONS TO RETRIEVE THE LATEST RTMA DATA FOR GUAM

        '''

        def get_current_rtma_data(current_time, parameter):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASET FOR A PARAMETER SPECIFIED BY THE USER
        
            IF THE DATASET FOR THE CURRENT TIME IS UNAVAILABLE THE FUNCTION WILL TRY TO RETURN THE MOST RECENT DATASET IN THE PAST 4 HOURS
        
            IF THE USER HAS A SYNTAX ERROR THE LINK TO THE UCAR THREDDS OPENDAP PARAMETER LIST WILL BE DISPLAYED
        
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            CURRENT RTMA DATASET FOR THE PARAMETER DEFINED BY THE USER
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
        
            for i in range(1,5):
                new_time = current_time - timedelta(hours=i)
                times.append(new_time)
        
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+current_time.strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+current_time.strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_parameter = rtma_data[parameter].squeeze()

                print("Data retrieval for " + current_time.strftime('%m/%d/%Y %H00 UTC') + " is successful")

                time = current_time
                
                return rtma_parameter, time
                
            except Exception as e:
        
                print(parameter + " Data is unavailiable for "+current_time.strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[0].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_parameter = rtma_data[parameter].squeeze()
        
                    print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                    time = time[0]
                    
                    return rtma_parameter, time
        
                except Exception as a:
        
                    print(parameter + " Data is unavailiable for "+times[0].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[1].strftime('%m/%d/%Y %H00 UTC'))
                   
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_parameter = rtma_data[parameter].squeeze()
            
                        print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                        time = times[1]
                        
                        return rtma_parameter, time
        
        
                    except Exception as b:
                                    
                        print(parameter + " Data is unavailiable for "+times[1].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[2].strftime('%m/%d/%Y %H00 UTC'))
        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_parameter = rtma_data[parameter].squeeze()
            
                            print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                            time = times[2]
                            
                            return rtma_parameter, time
        
                        except Exception as c:
                                    
                            print(parameter + " Data is unavailiable for "+times[3].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[3].strftime('%m/%d/%Y %H00 UTC'))
        
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_parameter = rtma_data[parameter].squeeze()
                
                                print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")
                                time = times[3]
                                
                                return rtma_parameter, time
                            
                        
                            except syntaxError as k:
                                error = info.syntax_error()
        
                                return error
        
        
        def get_rtma_data_24_hour_difference(current_time, parameter):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASET FOR A PARAMETER SPECIFIED BY THE USER
        
            THIS FUNCTION ALSO RETRIEVES THE DATASET FROM 24 HOURS PRIOR TO THE CURRENT DATASET FOR A 24 HOUR COMPARISON
        
            THE 24 HOUR COMPARISON IS SUBTRACTING THE CURRENT VALUES FROM THE VALUES FROM 24 HOURS AGO TO SHOW THE CHANGE
            
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            THE DIFFERENCE IN VALUES BETWEEN THE CURRENT DATASET AND DATASET FROM 24 HOURS AGO FOR THE PARAMETER DEFINED BY THE USER
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
            times_24 = []
        
            for i in range(0,5):
                new_time = current_time - timedelta(hours=i)
                old_time = new_time - timedelta(hours=24)
                times.append(new_time)
                times_24.append(old_time)
                
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_parameter = rtma_data[parameter].squeeze()
        
                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                rtma_parameter_24 = rtma_data_24[parameter].squeeze()
        
                print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                time = times[0]
                
                return rtma_parameter - rtma_parameter_24, time
                
            except Exception as e:
                
                print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[0].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                print("Will try to download the most recent datasets from "+times[1].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[1].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_parameter = rtma_data[parameter].squeeze()
            
                    rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data_24 = rtma_data_24.metpy.parse_cf()
                    rtma_parameter_24 = rtma_data_24[parameter].squeeze()
            
                    print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                    time = times[1]
                    
                    return rtma_parameter - rtma_parameter_24, time
             
                except Exception as a:
        
                    print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[1].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                    print("Will try to download the most recent datasets from "+times[2].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[2].strftime('%m/%d/%Y %H00 UTC'))
                    
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_parameter = rtma_data[parameter].squeeze()
                
                        rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data_24 = rtma_data_24.metpy.parse_cf()
                        rtma_parameter_24 = rtma_data_24[parameter].squeeze()
                
                        print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                        time = times[2]
                        
                        return rtma_parameter - rtma_parameter_24, time
        
        
                    except Exception as b:
                                    
                        print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[2].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                        print("Will try to download the most recent datasets from "+times[3].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[3].strftime('%m/%d/%Y %H00 UTC'))
                        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_parameter = rtma_data[parameter].squeeze()
                    
                            rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data_24 = rtma_data_24.metpy.parse_cf()
                            rtma_parameter_24 = rtma_data_24[parameter].squeeze()
                    
                            print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                            time = times[3]
                            
                            return rtma_parameter - rtma_parameter_24, time
        
                        except Exception as c:
                                    
                            print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " and/or " + times_24[3].strftime('%m/%d/%Y %H00 UTC') + " is unsuccessful")
                            print("Will try to download the most recent datasets from "+times[4].strftime('%m/%d/%Y %H00 UTC')+ " and " + times_24[4].strftime('%m/%d/%Y %H00 UTC'))
                            
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_parameter = rtma_data[parameter].squeeze()
                        
                                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                                rtma_parameter_24 = rtma_data_24[parameter].squeeze()
                        
                                print("Data retrieval for " + times[4].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[4].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                                time = times[4]
                                
                                return rtma_parameter - rtma_parameter_24, time
                                      
                        
                            except syntaxError as k:
                                error = info.syntax_error()
        
                                return error
        
        
        def get_current_rtma_relative_humidity_data(current_time):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASETS FOR TEMPERATURE AND DEWPOINT
        
            THIS FUNCTION THEN CALCULATES A RELATIVE HUMIDITY DATASET USING METPY.CALC FROM THE TEMPERATURE AND DEWPOINT DATASETS
        
            IF THE DATASET FOR THE CURRENT TIME IS UNAVAILABLE THE FUNCTION WILL TRY TO RETURN THE MOST RECENT DATASET IN THE PAST 4 HOURS
        
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            CURRENT RTMA DATASET FOR RELATIVE HUMIDITY
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
        
            for i in range(0,5):
                new_time = current_time - timedelta(hours=i)
                times.append(new_time)
        
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
        
                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                print("Data retrieval for " + times[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                time = times[0]
                
                return rtma_rh *100, time
                
            except Exception as e:
        
                print("Relative Humidity Data is unavailiable for "+times[0].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[1].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                    rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
            
                    rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                    print("Data retrieval for " + times[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                    time = times[1]
                    
                    return rtma_rh *100, time
          
                except Exception as a:
        
                    print("Relative Humidity data is unavailiable for "+times[1].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[2].strftime('%m/%d/%Y %H00 UTC'))
                    
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                        rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                
                        rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                        print("Data retrieval for " + times[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                        time = times[2]
                        
                        return rtma_rh *100, time
        
                    except Exception as b:
                                    
                        print("Relative Humidity data is unavailiable for "+times[2].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[3].strftime('%m/%d/%Y %H00 UTC'))
                        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                            rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                    
                            rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                            print("Data retrieval for " + times[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                            time = times[3]
                            
                            return rtma_rh *100, time
        
                        except Exception as c:
                                    
                            print("Relative Humidity data is unavailiable for "+times[3].strftime('%m/%d/%Y %H00 UTC')+ "\nWill try to download the most recent dataset from "+times[4].strftime('%m/%d/%Y %H00 UTC'))
                            
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                        
                                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                                print("Data retrieval for " + times[4].strftime('%m/%d/%Y %H00 UTC') + " is successful")
                                time = times[4]
                                
                                return rtma_rh *100, time
                                       
                        
                            except Exception as k:
                                print("WARNING: Latest dataset is more than 4 hours old.\nQuitting - Please try again later.")
        
                                return None
        
        
        def get_rtma_relative_humidity_24_hour_difference_data(current_time):
        
            r"""
            THIS FUNCTION RETRIEVES THE LATEST 2.5KM X 2.5KM REAL TIME MESOSCALE ANALYSIS DATASETS FOR TEMPERATURE AND DEWPOINT AND THE CORRESPONDING DATASETS FROM 24 HOURS AGO
        
            THIS FUNCTION THEN CALCULATES A RELATIVE HUMIDITY DATASET USING METPY.CALC FROM THE TEMPERATURE AND DEWPOINT DATASETS
        
            IF THE DATASET FOR THE CURRENT TIME IS UNAVAILABLE THE FUNCTION WILL SEARCH FOR THE LATEST DATASET IN THE PAST 4 HOURS
        
            PYTHON PACKAGE DEPENDENCIES:
        
            1. SIPHON
            2. METPY
            3. DATETIME
        
            RETURNS:
        
            24 HOUR DIFFERENCE IN RELATIVE HUMIDITY
        
            COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        
            """
        
            times = []
            times_24 = []
        
            for i in range(0,5):
                new_time = current_time - timedelta(hours=i)
                old_time = new_time - timedelta(hours=24)
                times.append(new_time)
                times_24.append(old_time)
        
            try:
                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data = rtma_data.metpy.parse_cf()
                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
        
                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
        
                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[0].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
        
                rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                print("Data retrieval for both " + times[0].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[0].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                time = times[0]
                
                return (rtma_rh - rtma_rh_24) *100, time
                
            except Exception as e:
        
                print("Relative Humidity Data is unavailiable for "+times[0].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[0].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[1].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[1].strftime('%m/%d/%Y %H00 UTC'))
                
                try:
                    rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data = rtma_data.metpy.parse_cf()
                    rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                    rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
            
                    rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
            
                    rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                    rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[1].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                    rtma_data_24 = rtma_data_24.metpy.parse_cf()
                    rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                    rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
            
                    rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                    print("Data retrieval for both " + times[1].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[1].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                    time = times[1]
                    
                    return (rtma_rh - rtma_rh_24) *100, time 
                    
                except Exception as a:
        
                    print("Relative Humidity Data is unavailiable for "+times[1].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[1].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[2].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[2].strftime('%m/%d/%Y %H00 UTC'))
                    
                    try:
                        rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data = rtma_data.metpy.parse_cf()
                        rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                        rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                
                        rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                
                        rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                        rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[2].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                        rtma_data_24 = rtma_data_24.metpy.parse_cf()
                        rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                        rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                
                        rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                        print("Data retrieval for both " + times[2].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[2].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                        time = times[2]
                        
                        return (rtma_rh - rtma_rh_24) *100, time 
                        
                    except Exception as b:
                                    
                        print("Relative Humidity Data is unavailiable for "+times[2].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[2].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[3].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[3].strftime('%m/%d/%Y %H00 UTC'))
                        
                        try:
                            rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data = rtma_data.metpy.parse_cf()
                            rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                            rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                    
                            rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                    
                            rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                            rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[3].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                            rtma_data_24 = rtma_data_24.metpy.parse_cf()
                            rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                            rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                    
                            rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                            print("Data retrieval for both " + times[3].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[3].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                            time = times[3]
                            
                            return (rtma_rh - rtma_rh_24) *100, time 
         
                        except Exception as c:
                                    
                            print("Relative Humidity Data is unavailiable for "+times[3].strftime('%m/%d/%Y %H00 UTC')+ " and/or " +times_24[3].strftime('%m/%d/%Y %H00 UTC')+"\nWill try to download the most recent dataset from "+times[4].strftime('%m/%d/%Y %H00 UTC') + " and " +times_24[4].strftime('%m/%d/%Y %H00 UTC'))
                    
                            try:
                                rtma_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data = rtma_cat.datasets['RTMA_GUAM_2p5km_'+times[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data = rtma_data.metpy.parse_cf()
                                rtma_temp = rtma_data['Temperature_Analysis_height_above_ground'].squeeze()
                                rtma_dwpt = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                        
                                rtma_rh = mpcalc.relative_humidity_from_dewpoint(rtma_temp, rtma_dwpt)
                        
                                rtma_cat_24 = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/GUAM_2p5km/RTMA_GUAM_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2/catalog.xml')
                                rtma_data_24 = rtma_cat_24.datasets['RTMA_GUAM_2p5km_'+times_24[4].strftime('%Y%m%d_%H00')+'.grib2'].remote_access(use_xarray=True)
                                rtma_data_24 = rtma_data_24.metpy.parse_cf()
                                rtma_temp_24 = rtma_data_24['Temperature_Analysis_height_above_ground'].squeeze()
                                rtma_dwpt_24 = rtma_data_24['Dewpoint_temperature_Analysis_height_above_ground'].squeeze()
                        
                                rtma_rh_24 = mpcalc.relative_humidity_from_dewpoint(rtma_temp_24, rtma_dwpt_24)
                                print("Data retrieval for both " + times[4].strftime('%m/%d/%Y %H00 UTC') + " and " + times_24[4].strftime('%m/%d/%Y %H00 UTC') + " is successful")

                                time = times[4]
                                
                                return (rtma_rh - rtma_rh_24) *100, time 
                
                            except Exception as k:
                                print("WARNING: Latest dataset is more than 4 hours old.\nQuitting - Please try again later.")
        
                                return None


    class METARs:
        
        r'''
        THIS CLASS HOSTS FUNCTIONS TO DOWNLOAD METAR DATA

        '''

        def get_METAR_Data(current_time, plot_projection, mask):

            r'''

            THIS FUNCTION DOWNLOADS THE LATEST METAR DATA FROM THE UCAR THREDDS SERVER AND RETURNS THE METAR DATA

            (C) METEOROLOGIST ERIC J. DREWITZ 2023

            '''
            metar_time = current_time
            
            # Pings server for airport data
            airports_df = pd.read_csv(get_test_data('airport-codes.csv'))
            
            # Queries our airport types (airport sizes)
            airports_df = airports_df[(airports_df['type'] == 'large_airport') | (airports_df['type'] == 'medium_airport') | (airports_df['type'] == 'small_airport')]
            
            # Accesses the METAR data
            try:
                metar_cat = TDSCatalog('https://thredds-test.unidata.ucar.edu/thredds/catalog/noaaport/text/metar/catalog.xml')
            
            except Exception as e:
                metar_cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/noaaport/text/metar/catalog.xml')
                
            # Opens METAR file
            metar_file = metar_cat.datasets.filter_time_nearest(metar_time).remote_open()
            
            # Decodes bytes into strings
            metar_text = StringIO(metar_file.read().decode('latin-1'))
            
            # Parses through data
            sfc_data = parse_metar_file(metar_text, year=metar_time.year, month=metar_time.month)
            sfc_units = sfc_data.units
            
            # Creates dataframe
            sfc_data = sfc_data[sfc_data['station_id'].isin(airports_df['ident'])]
            
            sfc_data = pandas_dataframe_to_unit_arrays(sfc_data, sfc_units)
            
            sfc_data['u'], sfc_data['v'] = mpcalc.wind_components(sfc_data['wind_speed'], sfc_data['wind_direction'])
            
            sfc_data_u_kt = sfc_data['u'].to('kts')
            sfc_data_v_kt = sfc_data['v'].to('kts')
            
            sfc_data_rh = mpcalc.relative_humidity_from_dewpoint(sfc_data['air_temperature'], sfc_data['dew_point_temperature'])
            
            
            locs = plot_projection.transform_points(ccrs.PlateCarree(), sfc_data['longitude'].m, sfc_data['latitude'].m)
            
            # Creates mask for plotting METAR obs
            sfc_data_mask = mpcalc.reduce_point_density(locs[:, :2], mask)

            print("METAR Data successfully retrieved for " + metar_time.strftime('%m/%d/%Y %H00 UTC'))
            return sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time


        def latest_metar_time(current_time):

            r'''
            THIS FUNCTION SERVES AS A TIMECHECK FOR THE LATEST TIME A COMPLETE DATASET OF METAR DATA. IF THE PROGRAM RUNS AFTER 30 MINUTES PAST THE HOUR, NEW DATA TRICKLES IN AND IS VERY SPARSE SO THIS ENSURES WE HAVE THE LATEST FULL DATASET. 

            (C) METEOROLOGIST ERIC J. DREWITZ

            '''

            
            runtime = current_time
            minute = runtime.minute
            # Times for METAR reports
            if runtime.minute <30:
                metar_time = datetime.utcnow() 
            if runtime.minute >=30:
                metar_time = datetime.utcnow() - timedelta(minutes=minute)

            return metar_time

            


        def RTMA_Synced_With_METAR(parameter, current_time, mask):

            r'''

            THIS FUNCTION RETURNS THE LATEST RTMA DATASET WITH THE LATEST METAR DATASET AND SYNCS UP BOTH DATASETS TO BE REPRESENTATIVE OF THE SAME TIME SINCE THE METAR DATA IS AVAILIABLE MUCH QUICKER THAN THE RTMA DATA. THIS ALLOWS USERS TO OVERLAY METAR DATA ONTO RTMA DATA AND HAVE THE TIMES BETWEEN BOTH DATASETS MATCH. 

            (C) METEOROLOGIST ERIC J. DREWITZ 2023

            '''

            parameter = parameter
            current_time = current_time
            mask = mask

            metar_time = UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.latest_metar_time(current_time)

            rtma_data, rtma_time = UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(current_time, parameter)

            plot_projection = rtma_data.metpy.cartopy_crs
            
            new_metar_time = parsers.checks.check_RTMA_vs_METAR_Times(rtma_time, metar_time)

            sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised = UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.get_METAR_Data(new_metar_time, plot_projection, mask)

            return rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_projection


        def RTMA_Relative_Humidity_Synced_With_METAR(current_time, mask):

            r'''
            THIS FUNCTION RETURNS THE LATEST RTMA RELATIVE HUMIDITY DATASET WITH THE LATEST METAR DATASET AND SYNCS UP BOTH DATASETS TO BE REPRESENTATIVE OF THE SAME TIME SINCE THE METAR DATA IS AVAILIABLE MUCH QUICKER THAN THE RTMA DATA. THIS ALLOWS USERS TO OVERLAY METAR DATA ONTO RTMA DATA AND HAVE THE TIMES BETWEEN BOTH DATASETS MATCH. 

            (C) METEOROLOGIST ERIC J. DREWITZ 2023
            '''

            current_time = current_time
            mask = mask

            metar_time = UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.latest_metar_time(current_time)

            rtma_data, rtma_time = UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_relative_humidity_data(current_time)

            plot_projection = rtma_data.metpy.cartopy_crs
            
            new_metar_time = parsers.checks.check_RTMA_vs_METAR_Times(rtma_time, metar_time)

            sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised = UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.get_METAR_Data(new_metar_time, plot_projection, mask)

            return rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_projection

            
class NOMADS_OPENDAP_Downloads:

    r'''
    THIS CLASS RETRIEVES DATA FROM THE NOMADS OPENDAP

    '''


    class RTMA_Alaska:

        r'''
        THIS CLASS HOSTS FUNCTIONS THAT RETRIEVE THE REAL TIME MESOSCALE ANALYSIS DATA FOR ALASKA
        
        '''

        def get_RTMA_Data_single_parameter(current_time, parameter):

            r'''

            THIS FUNCTION RETRIEVES THE RTMA DATA FOR A SINGLE PARAMETER

            (C) METEOROLOGIST ERIC J. DREWITZ 2023

            '''
            param = parameter
            
            times = []
            for i in range(0, 5):
                time = pd.to_datetime(current_time - timedelta(hours=i))
                times.append(time)

            url_0 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[0].strftime('%Y%m%d')+'/akrtma_anl_'+times[0].strftime('%H')+'z'
            url_1 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[1].strftime('%Y%m%d')+'/akrtma_anl_'+times[1].strftime('%H')+'z'
            url_2 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[2].strftime('%Y%m%d')+'/akrtma_anl_'+times[2].strftime('%H')+'z'
            url_3 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[3].strftime('%Y%m%d')+'/akrtma_anl_'+times[3].strftime('%H')+'z'
            url_4 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[4].strftime('%Y%m%d')+'/akrtma_anl_'+times[4].strftime('%H')+'z'

            try:
                ds = xr.open_dataset(url_0, engine='netcdf4')
                print("Data was successfully retrieved for " + times[0].strftime('%m/%d/%Y %HZ'))
                strtime = times[0]
                
            except Exception as a:
                try:
                    print("There is no data for " + times[0].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[1].strftime('%m/%d/%Y %HZ'))
                    ds = xr.open_dataset(url_1, engine='netcdf4')
                    print("Data was successfully retrieved for " + times[1].strftime('%m/%d/%Y %HZ'))
                    strtime = times[1]
                    
                except Exception as b:
                        try:
                            print("There is no data for " + times[1].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[2].strftime('%m/%d/%Y %HZ'))
                            ds = xr.open_dataset(url_2, engine='netcdf4')
                            print("Data was successfully retrieved for " + times[2].strftime('%m/%d/%Y %HZ'))
                            strtime = times[2]
                            
                        except Exception as c:
                            try:
                                print("There is no data for " + times[2].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[3].strftime('%m/%d/%Y %HZ'))
                                ds = xr.open_dataset(url_3, engine='netcdf4')
                                print("Data was successfully retrieved for " + times[3].strftime('%m/%d/%Y %HZ'))
                                strtime = times[3]
                            except Exception as d:
    
                                try:
                                    print("There is no data for " + times[3].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[4].strftime('%m/%d/%Y %HZ'))
                                    ds = xr.open_dataset(url_4, engine='netcdf4')
                                    print("Data was successfully retrieved for " + times[4].strftime('%m/%d/%Y %HZ'))
                                    strtime = times[4]
                                    
                                except Exception as e:
                                    print("The latest dataset is over 4 hours old which isn't current. Please try again later.")
            try:
                parameter_data = ds[parameter]
                lat = parameter_data['lat']
                lon = parameter_data['lon']
                
                lat_vals = lat[:].squeeze()
                lon_vals = lon[:].squeeze()

                data_to_plot = parameter_data[0, :, :]
                
                return lon_vals, lat_vals, strtime, data_to_plot
                
            except Exception as f:
                error = info.invalid_parameter_NOMADS_RTMA_Alaska()
                print(error)

        def get_RTMA_Data_24_hour_change_single_parameter(current_time, parameter):

            r'''

            THIS FUNCTION RETRIEVES THE RTMA DATA FOR A SINGLE PARAMETER

            (C) METEOROLOGIST ERIC J. DREWITZ 2023

            '''
            param = parameter
            times = []
            times_24 = []
            for i in range(0, 5):
                time = pd.to_datetime(current_time - timedelta(hours=i))
                times.append(time)
                time_24 = pd.to_datetime(time - timedelta(hours=24))
                times_24.append(time_24)

            ### LATEST TIME URLS ###
            url_0 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[0].strftime('%Y%m%d')+'/akrtma_anl_'+times[0].strftime('%H')+'z'
            url_1 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[1].strftime('%Y%m%d')+'/akrtma_anl_'+times[1].strftime('%H')+'z'
            url_2 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[2].strftime('%Y%m%d')+'/akrtma_anl_'+times[2].strftime('%H')+'z'
            url_3 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[3].strftime('%Y%m%d')+'/akrtma_anl_'+times[3].strftime('%H')+'z'
            url_4 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[4].strftime('%Y%m%d')+'/akrtma_anl_'+times[4].strftime('%H')+'z'


            ### 24 HOURS AGO URLS ###
            url_5 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[0].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[0].strftime('%H')+'z'
            url_6 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[1].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[1].strftime('%H')+'z'
            url_7 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[2].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[2].strftime('%H')+'z'
            url_8 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[3].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[3].strftime('%H')+'z'
            url_9 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[4].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[4].strftime('%H')+'z'

            try:
                ds = xr.open_dataset(url_0, engine='netcdf4')
                print("Data was successfully retrieved for " + times[0].strftime('%m/%d/%Y %HZ'))
                ds_24 = xr.open_dataset(url_5, engine='netcdf4')
                print("Data was successfully retrieved for " + times_24[0].strftime('%m/%d/%Y %HZ'))
                time = times[0]
                time_24 = times_24[0]

            except Exception as a:
                try:
                    print("There is no data for " + times[0].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[1].strftime('%m/%d/%Y %HZ'))
                    ds = xr.open_dataset(url_1, engine='netcdf4')
                    print("Data was successfully retrieved for " + times[1].strftime('%m/%d/%Y %HZ'))
                    ds_24 = xr.open_dataset(url_6, engine='netcdf4')
                    print("Data was successfully retrieved for " + times_24[1].strftime('%m/%d/%Y %HZ'))
                    time = times[1]
                    time_24 = times_24[1]

                except Exception as b:
                        try:
                            print("There is no data for " + times[1].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[2].strftime('%m/%d/%Y %HZ'))
                            ds = xr.open_dataset(url_2, engine='netcdf4')
                            print("Data was successfully retrieved for " + times[2].strftime('%m/%d/%Y %HZ'))
                            ds_24 = xr.open_dataset(url_7, engine='netcdf4')
                            print("Data was successfully retrieved for " + times_24[2].strftime('%m/%d/%Y %HZ'))
                            time = times[2]
                            time_24 = times_24[2]

                        except Exception as c:
                            try:
                                print("There is no data for " + times[2].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[3].strftime('%m/%d/%Y %HZ'))
                                ds = xr.open_dataset(url_3, engine='netcdf4')
                                print("Data was successfully retrieved for " + times[3].strftime('%m/%d/%Y %HZ'))
                                ds_24 = xr.open_dataset(url_8, engine='netcdf4')
                                print("Data was successfully retrieved for " + times_24[3].strftime('%m/%d/%Y %HZ'))
                                time = times[3]
                                time_24 = times_24[3]
                            
                            except Exception as d:
    
                                try:
                                    print("There is no data for " + times[3].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[4].strftime('%m/%d/%Y %HZ'))
                                    ds = xr.open_dataset(url_4, engine='netcdf4')
                                    print("Data was successfully retrieved for " + times[4].strftime('%m/%d/%Y %HZ'))
                                    ds_24 = xr.open_dataset(url_9, engine='netcdf4')
                                    print("Data was successfully retrieved for " + times_24[4].strftime('%m/%d/%Y %HZ'))
                                    time = times[4]
                                    time_24 = times_24[4]
                                    
                                except Exception as e:
                                    print("The latest dataset is over 4 hours old which isn't current. Please try again later.")
            try:
                parameter_data = ds[parameter]
                lat = parameter_data['lat']
                lon = parameter_data['lon']
                
                lat_vals = lat[:].squeeze()
                lon_vals = lon[:].squeeze()

                parameter_data_24 = ds_24[parameter]

                if param == 'tmp2m' or param == 'dpt2m':
                    parameter_data = units('degF') * parameter_data
                    parameter_data_24 = units('degF') * parameter_data_24

                if param == 'wind10m' or param == 'gust10m' or param == 'ugrd10m' or param == 'vgrd10m':
                    parameter_data = units('knots') * parameter_data
                    parameter_data_24 = units('knots') * parameter_data_24

                if param == 'wdir10m':
                    parameter_data = units('degree') * parameter_data
                    parameter_data_24 = units('degree') * parameter_data_24

                if param == 'vissfc' or param == 'ceilceil':
                    parameter_data = units('meters') * parameter_data
                    parameter_data_24 = units('meters') * parameter_data_24

                if param == 'pressfc':
                    parameter_data = units('hPa') * parameter_data
                    parameter_data_24 = units('hPa') * parameter_data_24

                if param == 'tcdcclm':
                    parameter_data = units('percent') * parameter_data
                    parameter_data_24 = units('percent') * parameter_data_24

                data_to_plot = parameter_data[0, :, :] - parameter_data_24[0, :, :]
                
                return lon_vals, lat_vals, time, time_24, data_to_plot
                
            except Exception as f:
                error = info.invalid_parameter_NOMADS_RTMA_Alaska()
                print(error)

        
        def get_RTMA_relative_humidity(current_time):

            r'''
            THIS FUNCTION RETRIVES THE RTMA DATA FOR THE USUAL FIRE WEATHER PARAMETERS (TEMPERATURE, DEWPOINT, WIND SPEED AND RELATIVE HUMIDITY

            (C) METEOROLOGIST ERIC J. DREWITZ 2023

            '''

            
            times = []
            for i in range(0, 5):
                time = pd.to_datetime(current_time - timedelta(hours=i))
                times.append(time)

            url_0 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[0].strftime('%Y%m%d')+'/akrtma_anl_'+times[0].strftime('%H')+'z'
            url_1 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[1].strftime('%Y%m%d')+'/akrtma_anl_'+times[1].strftime('%H')+'z'
            url_2 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[2].strftime('%Y%m%d')+'/akrtma_anl_'+times[2].strftime('%H')+'z'
            url_3 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[3].strftime('%Y%m%d')+'/akrtma_anl_'+times[3].strftime('%H')+'z'
            url_4 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[4].strftime('%Y%m%d')+'/akrtma_anl_'+times[4].strftime('%H')+'z'

            try:
                ds = xr.open_dataset(url_0, engine='netcdf4')
                print("Data was successfully retrieved for " + times[0].strftime('%m/%d/%Y %HZ'))
                time = times[0]

            except Exception as a:
                try:
                    print("There is no data for " + times[0].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[1].strftime('%m/%d/%Y %HZ'))
                    ds = xr.open_dataset(url_1, engine='netcdf4')
                    print("Data was successfully retrieved for " + times[1].strftime('%m/%d/%Y %HZ'))
                    time = times[1]

                except Exception as b:
                        try:
                            print("There is no data for " + times[1].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[2].strftime('%m/%d/%Y %HZ'))
                            ds = xr.open_dataset(url_2, engine='netcdf4')
                            print("Data was successfully retrieved for " + times[2].strftime('%m/%d/%Y %HZ'))
                            time = times[2]

                        except Exception as c:
                            try:
                                print("There is no data for " + times[2].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[3].strftime('%m/%d/%Y %HZ'))
                                ds = xr.open_dataset(url_3, engine='netcdf4')
                                print("Data was successfully retrieved for " + times[3].strftime('%m/%d/%Y %HZ'))
                                time = times[3]

                            except Exception as d:
    
                                try:
                                    print("There is no data for " + times[3].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[4].strftime('%m/%d/%Y %HZ'))
                                    ds = xr.open_dataset(url_4, engine='netcdf4')
                                    print("Data was successfully retrieved for " + times[4].strftime('%m/%d/%Y %HZ'))
                                    time = times[4]
    
                                except Exception as e:
                                    print("The latest dataset is over 4 hours old which isn't current. Please try again later.")
            
            temperature = ds['tmp2m']
            lat = temperature['lat']
            lon = temperature['lon']
            
            lat_vals = lat[:].squeeze()
            lon_vals = lon[:].squeeze()
            
            dewpoint = ds['dpt2m']
            temperature_k = units('kelvin') * temperature
            dewpoint_k = units('kelvin') * dewpoint
            
            relative_humidity = mpcalc.relative_humidity_from_dewpoint(temperature_k, dewpoint_k)

            relative_humidity_to_plot = relative_humidity[0, :, :] 
                
            return lon_vals, lat_vals, time, relative_humidity_to_plot * 100


        def get_RTMA_Data_24_hour_change_relative_humidity(current_time):

            r'''

            THIS FUNCTION RETRIEVES THE RTMA DATA FOR A SINGLE PARAMETER

            (C) METEOROLOGIST ERIC J. DREWITZ 2023

            '''
            times = []
            times_24 = []
            for i in range(0, 5):
                time = pd.to_datetime(current_time - timedelta(hours=i))
                times.append(time)
                time_24 = pd.to_datetime(time - timedelta(hours=24))
                times_24.append(time_24)

            ### LATEST TIME URLS ###
            url_0 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[0].strftime('%Y%m%d')+'/akrtma_anl_'+times[0].strftime('%H')+'z'
            url_1 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[1].strftime('%Y%m%d')+'/akrtma_anl_'+times[1].strftime('%H')+'z'
            url_2 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[2].strftime('%Y%m%d')+'/akrtma_anl_'+times[2].strftime('%H')+'z'
            url_3 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[3].strftime('%Y%m%d')+'/akrtma_anl_'+times[3].strftime('%H')+'z'
            url_4 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times[4].strftime('%Y%m%d')+'/akrtma_anl_'+times[4].strftime('%H')+'z'


            ### 24 HOURS AGO URLS ###
            url_5 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[0].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[0].strftime('%H')+'z'
            url_6 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[1].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[1].strftime('%H')+'z'
            url_7 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[2].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[2].strftime('%H')+'z'
            url_8 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[3].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[3].strftime('%H')+'z'
            url_9 = 'http://nomads.ncep.noaa.gov:80/dods/akrtma/akrtma'+times_24[4].strftime('%Y%m%d')+'/akrtma_anl_'+times_24[4].strftime('%H')+'z'

            try:
                ds = xr.open_dataset(url_0, engine='netcdf4')
                print("Data was successfully retrieved for " + times[0].strftime('%m/%d/%Y %HZ'))
                ds_24 = xr.open_dataset(url_5, engine='netcdf4')
                print("Data was successfully retrieved for " + times_24[0].strftime('%m/%d/%Y %HZ'))
                time = times[0]
                time_24 = times_24[0]

            except Exception as a:
                try:
                    print("There is no data for " + times[0].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[1].strftime('%m/%d/%Y %HZ'))
                    ds = xr.open_dataset(url_1, engine='netcdf4')
                    print("Data was successfully retrieved for " + times[1].strftime('%m/%d/%Y %HZ'))
                    ds_24 = xr.open_dataset(url_6, engine='netcdf4')
                    print("Data was successfully retrieved for " + times_24[1].strftime('%m/%d/%Y %HZ'))
                    time = times[1]
                    time_24 = times_24[1]

                except Exception as b:
                        try:
                            print("There is no data for " + times[1].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[2].strftime('%m/%d/%Y %HZ'))
                            ds = xr.open_dataset(url_2, engine='netcdf4')
                            print("Data was successfully retrieved for " + times[2].strftime('%m/%d/%Y %HZ'))
                            ds_24 = xr.open_dataset(url_7, engine='netcdf4')
                            print("Data was successfully retrieved for " + times_24[2].strftime('%m/%d/%Y %HZ'))
                            time = times[2]
                            time_24 = times_24[2]

                        except Exception as c:
                            try:
                                print("There is no data for " + times[2].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[3].strftime('%m/%d/%Y %HZ'))
                                ds = xr.open_dataset(url_3, engine='netcdf4')
                                print("Data was successfully retrieved for " + times[3].strftime('%m/%d/%Y %HZ'))
                                ds_24 = xr.open_dataset(url_8, engine='netcdf4')
                                print("Data was successfully retrieved for " + times_24[3].strftime('%m/%d/%Y %HZ'))
                                time = times[3]
                                time_24 = times_24[3]
                                
                            except Exception as d:
    
                                try:
                                    print("There is no data for " + times[3].strftime('%m/%d/%Y %HZ') + " trying to retrieve data from the previous analysis at " + times[4].strftime('%m/%d/%Y %HZ'))
                                    ds = xr.open_dataset(url_4, engine='netcdf4')
                                    print("Data was successfully retrieved for " + times[4].strftime('%m/%d/%Y %HZ'))
                                    ds_24 = xr.open_dataset(url_9, engine='netcdf4')
                                    print("Data was successfully retrieved for " + times_24[4].strftime('%m/%d/%Y %HZ'))
                                    time = times[4]
                                    time_24 = times_24[4]
                                    
                                except Exception as e:
                                    print("The latest dataset is over 4 hours old which isn't current. Please try again later.")
            temperature = ds['tmp2m']
            temperature_24 = ds_24['tmp2m']
            lat = temperature['lat']
            lon = temperature['lon']
            
            lat_vals = lat[:].squeeze()
            lon_vals = lon[:].squeeze()
            
            dewpoint = ds['dpt2m']
            dewpoint_24 = ds_24['dpt2m']
            temperature_k = units('kelvin') * temperature
            dewpoint_k = units('kelvin') * dewpoint
            temperature_k_24 = units('kelvin') * temperature_24
            dewpoint_k_24 = units('kelvin') * dewpoint_24
            
            relative_humidity = mpcalc.relative_humidity_from_dewpoint(temperature_k, dewpoint_k)

            relative_humidity_24 = mpcalc.relative_humidity_from_dewpoint(temperature_k_24, dewpoint_k_24)

            diff = relative_humidity[0, :, :] - relative_humidity_24[0, :, :]
                
            return lon_vals, lat_vals, time, time_24, diff * 100



