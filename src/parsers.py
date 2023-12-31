# THIS SCRIPT HAS FUNCTIONS THAT PARSE THROUGH GRIB FILES THAT CONTAIN WEATHER DATA TO RETURN SORTED AND ORGANIZED DATA ARRAYS FOR GRAPHICAL CREATION/PLOTTING
#
# DEPENDENCIES INCLUDE:
# 1. PYGRIB
# 2. DATETIME 
#
#  (C) METEOROLOGIST ERIC J. DREWITZ
#               USDA/USFS

##### IMPORTS NEEDED PYTHON MODULES #######

import pygrib
import numpy as np

from datetime import datetime, timedelta
from metpy.units import units

class NDFD:

    r'''
    THIS CLASS HOSTS A VARIETY OF FUNCTIONS TO PARSE THROUGH THE NWS NDFD GRIB DATA

    '''
    

    def GRIB_temperature_conversion(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files):
    
        r'''
        THIS FUNCTION CONVERTS THE TEMPERATURE VALUES FROM KELVIN TO FAHRENHEIT FOR OUR PLOT
    
        RETURNS: TEMPERATURE VALUES IN FAHRENHEIT
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
    
        frac = 9/5
        if count_of_GRIB_files == 1:
            grb_1_vals = first_GRIB_file.values
            grb_1_vals_k = units('kelvin') * grb_1_vals
            grb_1_vals_f = grb_1_vals_k.to('degF')
    
            grb_2_vals = None
            grb_3_vals = None
            grb_4_vals = None
            grb_5_vals = None
                
            return grb_1_vals_f, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
    
        if count_of_GRIB_files == 2:
            grb_1_vals = first_GRIB_file.values
            grb_2_vals = second_GRIB_file.values
            
            grb_1_vals_k = units('kelvin') * grb_1_vals
            grb_1_vals_f = grb_1_vals_k.to('degF')

            grb_2_vals_k = units('kelvin') * grb_2_vals
            grb_2_vals_f = grb_2_vals_k.to('degF')

            grb_3_vals = None
            grb_4_vals = None
            grb_5_vals = None
                
            return grb_1_vals_f, grb_2_vals_f, grb_3_vals, grb_4_vals, grb_5_vals
    
        if count_of_GRIB_files == 3:
            grb_1_vals = first_GRIB_file.values
            grb_2_vals = second_GRIB_file.values
            grb_3_vals = third_GRIB_file.values
            
            grb_1_vals_k = units('kelvin') * grb_1_vals
            grb_1_vals_f = grb_1_vals_k.to('degF')

            grb_2_vals_k = units('kelvin') * grb_2_vals
            grb_2_vals_f = grb_2_vals_k.to('degF')

            grb_3_vals_k = units('kelvin') * grb_3_vals
            grb_3_vals_f = grb_3_vals_k.to('degF')
    
            grb_4_vals = None
            grb_5_vals = None
    
            return grb_1_vals_f, grb_2_vals_f, grb_3_vals_f, grb_4_vals, grb_5_vals
    
        if count_of_GRIB_files == 4:
            grb_1_vals = first_GRIB_file.values
            grb_2_vals = second_GRIB_file.values
            grb_3_vals = third_GRIB_file.values
            grb_4_vals = fourth_GRIB_file.values
    
            grb_1_vals_k = units('kelvin') * grb_1_vals
            grb_1_vals_f = grb_1_vals_k.to('degF')

            grb_2_vals_k = units('kelvin') * grb_2_vals
            grb_2_vals_f = grb_2_vals_k.to('degF')

            grb_3_vals_k = units('kelvin') * grb_3_vals
            grb_3_vals_f = grb_3_vals_k.to('degF')

            grb_4_vals_k = units('kelvin') * grb_4_vals
            grb_4_vals_f = grb_4_vals_k.to('degF')            
    
            grb_5_vals = None
                    
            return grb_1_vals_f, grb_2_vals_f, grb_3_vals_f, grb_4_vals_f, grb_5_vals
    
        if count_of_GRIB_files >= 5:
            grb_1_vals = first_GRIB_file.values
            grb_2_vals = second_GRIB_file.values
            grb_3_vals = third_GRIB_file.values
            grb_4_vals = fourth_GRIB_file.values
            grb_5_vals = fifth_GRIB_file.values
            
            grb_1_vals_k = units('kelvin') * grb_1_vals
            grb_1_vals_f = grb_1_vals_k.to('degF')

            grb_2_vals_k = units('kelvin') * grb_2_vals
            grb_2_vals_f = grb_2_vals_k.to('degF')

            grb_3_vals_k = units('kelvin') * grb_3_vals
            grb_3_vals_f = grb_3_vals_k.to('degF')

            grb_4_vals_k = units('kelvin') * grb_4_vals
            grb_4_vals_f = grb_4_vals_k.to('degF')

            grb_5_vals_k = units('kelvin') * grb_5_vals
            grb_5_vals_f = grb_5_vals_k.to('degF')            
                    
            return grb_1_vals_f, grb_2_vals_f, grb_3_vals_f, grb_4_vals_f, grb_5_vals_f
    
    
    def GRIB_parameter_check_temperature(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files, parameter):
    
        r'''
        THIS FUNCTION IS SPECIFICALLY FOR THE CUSTOM GENERIC NWS FORECAST GRAPHIC
    
        THIS FUNCTION CHECKS TO SEE IF THE PARAMETER BEING USED IS FOR TEMPERATURE SO WE CAN PERFORM THE KELVIN TO FAHRENHEIT CONVERSION IF NEEDED.
    
        IF THE PARAMETER IS NOT TEMPERATURE, THIS FUNCTION WILL RETURN THE VALUES WITHIN THE GRIB FILE AS THEY ARE
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
    
        if parameter == 'ds.maxt.bin' or parameter == 'ds.mint.bin':
            frac = 9/5
            if count_of_GRIB_files == 1:
                grb_1_vals = first_GRIB_file.values
                celsius = grb_1_vals - 273.15
                fahrenheit = (frac * celsius) + 32
                grb_1_vals = fahrenheit
        
                grb_2_vals = None
                grb_3_vals = None
                grb_4_vals = None
                grb_5_vals = None
                    
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
        
            if count_of_GRIB_files == 2:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                
                celsius_1 = grb_1_vals - 273.15
                fahrenheit_1 = (frac * celsius_1) + 32
                grb_1_vals = fahrenheit_1
                    
                celsius_2 = grb_2_vals - 273.15
                fahrenheit_2 = (frac * celsius_2) + 32
                grb_2_vals = fahrenheit_2
        
                grb_3_vals = None
                grb_4_vals = None
                grb_5_vals = None
                    
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
        
            if count_of_GRIB_files == 3:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                grb_3_vals = third_GRIB_file.values
                
                celsius_1 = grb_1_vals - 273.15
                fahrenheit_1 = (frac * celsius_1) + 32
                grb_1_vals = fahrenheit_1
                    
                celsius_2 = grb_2_vals - 273.15
                fahrenheit_2 = (frac * celsius_2) + 32
                grb_2_vals = fahrenheit_2
        
                celsius_3 = grb_3_vals - 273.15
                fahrenheit_3 = (frac * celsius_3) + 32
                grb_3_vals = fahrenheit_3
        
                grb_4_vals = None
                grb_5_vals = None
        
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
        
            if count_of_GRIB_files == 4:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                grb_3_vals = third_GRIB_file.values
                grb_4_vals = fourth_GRIB_file.values
        
                celsius_1 = grb_1_vals - 273.15
                fahrenheit_1 = (frac * celsius_1) + 32
                grb_1_vals = fahrenheit_1
                    
                celsius_2 = grb_2_vals - 273.15
                fahrenheit_2 = (frac * celsius_2) + 32
                grb_2_vals = fahrenheit_2
        
                celsius_3 = grb_3_vals - 273.15
                fahrenheit_3 = (frac * celsius_3) + 32
                grb_3_vals = fahrenheit_3
        
                celsius_4 = grb_4_vals - 273.15
                fahrenheit_4 = (frac * celsius_4) + 32
                grb_4_vals = fahrenheit_4
        
                grb_5_vals = None
                        
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
            
            if count_of_GRIB_files >= 5:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                grb_3_vals = third_GRIB_file.values
                grb_4_vals = fourth_GRIB_file.values
                grb_5_vals = fifth_GRIB_file.values
                
                celsius_1 = grb_1_vals - 273.15
                fahrenheit_1 = (frac * celsius_1) + 32
                grb_1_vals = fahrenheit_1
                    
                celsius_2 = grb_2_vals - 273.15
                fahrenheit_2 = (frac * celsius_2) + 32
                grb_2_vals = fahrenheit_2
        
                celsius_3 = grb_3_vals - 273.15
                fahrenheit_3 = (frac * celsius_3) + 32
                grb_3_vals = fahrenheit_3
        
                celsius_4 = grb_4_vals - 273.15
                fahrenheit_4 = (frac * celsius_4) + 32
                grb_4_vals = fahrenheit_4
        
                celsius_5 = grb_5_vals - 273.15
                fahrenheit_5 = (frac * celsius_5) + 32
                grb_5_vals = fahrenheit_5
                        
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
    
        else:
            if count_of_GRIB_files == 1:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = None
                grb_3_vals = None
                grb_4_vals = None
                grb_5_vals = None
    
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
                
            if count_of_GRIB_files == 2:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                grb_3_vals = None
                grb_4_vals = None
                grb_5_vals = None
    
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
                
            if count_of_GRIB_files == 3:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                grb_3_vals = third_GRIB_file.values
                grb_4_vals = None
                grb_5_vals = None
    
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
                
            if count_of_GRIB_files == 4:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                grb_3_vals = third_GRIB_file.values
                grb_4_vals = fourth_GRIB_file.values
                grb_5_vals = None
    
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals
    
            if count_of_GRIB_files >= 5:
                grb_1_vals = first_GRIB_file.values
                grb_2_vals = second_GRIB_file.values
                grb_3_vals = third_GRIB_file.values
                grb_4_vals = fourth_GRIB_file.values
                grb_5_vals = fifth_GRIB_file.values
    
                return grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals


    def get_maximum_temperature_color_scale(directory_name):

        r'''
        THIS FUNCTION CREATES THE COLORSCALE FOR THE MAXIMUM TEMPERATURE FORECAST FOR EACH REGION OF THE CONUS FOR BOTH THE WARM AND COLD/COOL SEASON. EACH COLORSCALE IS REFLECTIVE OF EACH REGION SINCE A BROAD COLORSCALE WOULDN'T WORK SINCE FOR EXAMPLE A COLORSCALE FOR SOUTHERN CALIFORNIA WON'T BE VERY REPRESENTATIVE FOR PLOTTING TEMPERATURES IN THE NORTHEAST. THESE FUNCTIONS ALLOW THE CHANGING OF THE COLORSCALE BETWEEN REGIONS AND SEASONS SO USERS WON'T NEED TO WORRY ABOUT IT. 

        (C) METEOROLOGIST ERIC J. DREWITZ 2023

        '''

        dirName = directory_name
        
        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/':
            temp_scale_warm = np.arange(50, 135, 5)
            temp_scale_cool = np.arange(10, 105, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacnwest/':
            temp_scale_warm = np.arange(40, 125, 5)
            temp_scale_cool = np.arange(-10, 85, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nrockies/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crrocks/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nplains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.umissvly/':
            temp_scale_warm = np.arange(40, 125, 5)
            temp_scale_cool = np.arange(-30, 75, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.srockies/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crplains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crmissvy/':
            temp_scale_warm = np.arange(45, 135, 5)
            temp_scale_cool = np.arange(-20, 95, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.splains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.seast/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.smissvly/':
            temp_scale_warm = np.arange(60, 125, 5)
            temp_scale_cool = np.arange(0, 85, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.neast/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.ergrlake/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crgrlake/':
            temp_scale_warm = np.arange(30, 115, 5)
            temp_scale_cool = np.arange(-20, 75, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/':
            temp_scale_warm = np.arange(30, 135, 5)
            temp_scale_cool = np.arange(-30, 105, 5)

        return temp_scale_warm, temp_scale_cool


    def get_minimum_temperature_color_scale(directory_name):

        r'''
        THIS FUNCTION CREATES THE COLORSCALE FOR THE MINIMUM TEMPERATURE FORECAST FOR EACH REGION OF THE CONUS FOR BOTH THE WARM AND COLD/COOL SEASON. EACH COLORSCALE IS REFLECTIVE OF EACH REGION SINCE A BROAD COLORSCALE WOULDN'T WORK SINCE FOR EXAMPLE A COLORSCALE FOR SOUTHERN CALIFORNIA WON'T BE VERY REPRESENTATIVE FOR PLOTTING TEMPERATURES IN THE NORTHEAST. THESE FUNCTIONS ALLOW THE CHANGING OF THE COLORSCALE BETWEEN REGIONS AND SEASONS SO USERS WON'T NEED TO WORRY ABOUT IT. 

        (C) METEOROLOGIST ERIC J. DREWITZ 2023

        '''

        dirName = directory_name
        
        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/':
            temp_scale_warm = np.arange(30, 105, 5)
            temp_scale_cool = np.arange(-10, 75, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacnwest/':
            temp_scale_warm = np.arange(20, 95, 5)
            temp_scale_cool = np.arange(-20, 65, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nrockies/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crrocks/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nplains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.umissvly/':
            temp_scale_warm = np.arange(20, 85, 5)
            temp_scale_cool = np.arange(-30, 65, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.srockies/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crplains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crmissvy/':
            temp_scale_warm = np.arange(30, 95, 5)
            temp_scale_cool = np.arange(-20, 65, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.splains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.seast/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.smissvly/':
            temp_scale_warm = np.arange(50, 95, 5)
            temp_scale_cool = np.arange(-10, 75, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.neast/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.ergrlake/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crgrlake/':
            temp_scale_warm = np.arange(30, 85, 5)
            temp_scale_cool = np.arange(-30, 65, 5)

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/':
            temp_scale_warm = np.arange(20, 105, 5)
            temp_scale_cool = np.arange(-30, 75, 5)

        return temp_scale_warm, temp_scale_cool


    def get_extreme_heat_color_scale(directory_name):

        r'''
        THIS FUNCTION CREATES THE COLORSCALE FOR THE EXTREME HEAT FORECAST FOR EACH REGION OF THE CONUS FOR BOTH THE WARM AND COLD/COOL SEASON. EACH COLORSCALE IS REFLECTIVE OF EACH REGION SINCE A BROAD COLORSCALE WOULDN'T WORK SINCE FOR EXAMPLE A COLORSCALE FOR SOUTHERN CALIFORNIA WON'T BE VERY REPRESENTATIVE FOR PLOTTING TEMPERATURES IN THE NORTHEAST. THESE FUNCTIONS ALLOW THE CHANGING OF THE COLORSCALE BETWEEN REGIONS AND SEASONS SO USERS WON'T NEED TO WORRY ABOUT IT. 

        (C) METEOROLOGIST ERIC J. DREWITZ 2023

        '''

        dirName = directory_name
        
        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/':
            temp_scale_warm = np.arange(120, 140, 1)
            temp_scale_cool = np.arange(100, 125, 1)
            title_warm = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 120 \N{DEGREE SIGN}F)"
            title_cool = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 100 \N{DEGREE SIGN}F)"

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacnwest/':
            temp_scale_warm = np.arange(100, 125, 1)
            temp_scale_cool = np.arange(85, 115, 1)
            title_warm = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 100 \N{DEGREE SIGN}F)"
            title_cool = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 85 \N{DEGREE SIGN}F)"

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nrockies/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crrocks/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.nplains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.umissvly/':
            temp_scale_warm = np.arange(95, 125, 1)
            temp_scale_cool = np.arange(85, 115, 1)
            title_warm = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 95 \N{DEGREE SIGN}F)"
            title_cool = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 85 \N{DEGREE SIGN}F)"

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.srockies/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crplains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crmissvy/':
            temp_scale_warm = np.arange(95, 125, 1)
            temp_scale_cool = np.arange(85, 115, 1)
            title_warm = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 95 \N{DEGREE SIGN}F)"
            title_cool = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 85 \N{DEGREE SIGN}F)"           

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.splains/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.seast/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.smissvly/':
            temp_scale_warm = np.arange(100, 130, 1)
            temp_scale_cool = np.arange(85, 115, 1)
            title_warm = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 100 \N{DEGREE SIGN}F)"
            title_cool = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 85 \N{DEGREE SIGN}F)"

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.neast/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.ergrlake/' or dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.crgrlake/':
            temp_scale_warm = np.arange(90, 115, 1)
            temp_scale_cool = np.arange(75, 105, 1)
            title_warm = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 90 \N{DEGREE SIGN}F)"
            title_cool = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 75 \N{DEGREE SIGN}F)"

        if dirName == '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/':
            temp_scale_warm = np.arange(95, 140, 1)
            temp_scale_cool = np.arange(85, 125, 1)
            title_warm = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 95 \N{DEGREE SIGN}F)"
            title_cool = "National Weather Service Short-Term Forecast\nExtreme Heat (Maximum Temperature >= 85 \N{DEGREE SIGN}F)"

        return temp_scale_warm, temp_scale_cool, title_warm, title_cool
    
    
    def parse_SPC_GRIB_data(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files):
    
        r'''
    
        THIS FUNCTION PARSES THE SPC DATA AND RETURNS THE DIFFERENT DATA SUCH AS VALUES, VALID DATES/TIMES ETC. NEEDED FOR THE PLOT
        
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
        if count_of_GRIB_files == 1:
            grb_1_vals = first_GRIB_file.values
            grb_1_start = first_GRIB_file.validDate
            grb_1_end = grb_1_start + timedelta(hours=24)
                
            grb_2_start = None
            grb_2_end = None
            grb_2_vals = None
                
            grb_3_start = None
            grb_3_end = None
            grb_3_vals = None
    
        if count_of_GRIB_files == 2:
            grb_1_vals = first_GRIB_file.values
            grb_1_start = first_GRIB_file.validDate
            grb_1_end = grb_1_start + timedelta(hours=24)
            
            grb_2_start = second_GRIB_file.validDate
            grb_2_end = grb_2_start + timedelta(hours=24)
            grb_2_vals = second_GRIB_file.values
            
            grb_3_start = None
            grb_3_end = None
            grb_3_vals = None
    
        if count_of_GRIB_files == 3:
            grb_1_vals = first_GRIB_file.values
            grb_1_start = first_GRIB_file.validDate
            grb_1_end = grb_1_start + timedelta(hours=24)
            
            grb_2_vals = second_GRIB_file.values
            grb_2_start = second_GRIB_file.validDate
            grb_2_end = grb_2_start + timedelta(hours=24)
    
            grb_3_start = third_GRIB_file.validDate
            grb_3_end = grb_3_start + timedelta(days=7)
            grb_3_vals = third_GRIB_file.values
    
        if count_of_GRIB_files > 3:
            grb_1_vals = second_GRIB_file.values
            grb_1_start = second_GRIB_file.validDate
            grb_1_end = grb_1_start + timedelta(hours=24)
            
            grb_2_vals = third_GRIB_file.values
            grb_2_start = third_GRIB_file.validDate
            grb_2_end = grb_2_start + timedelta(days=6)
    
            grb_3_start = None
            grb_3_end = None
            grb_3_vals = None
    
        return grb_1_start, grb_1_end, grb_1_vals, grb_2_start, grb_2_end, grb_2_vals, grb_3_start, grb_3_end, grb_3_vals
    
    def sort_GRIB_files(GRIB_File_List, parameter):
        
        r'''
        THIS FUNCTION SORTS AND RETURNS THE INDIVIDUAL GRIB FILES IN THE DOWNLOADED DATASET. 
    
        THIS FUNCTION ALSO RETURNS THE COUNT OF THE NUMBER OF GRIB FILES IN THE DATASET.
    
        THIS FUNCTION IS TO BE USED IN THE PROGRAMMER'S CODE AFTER THE get_NWS_NDFD_grid_data(directory_name, parameter) FUNCTION IS USED
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
        count = 0
        for grb in GRIB_File_List:
            count = count + 1
        if count == 1:
            grb_1 = GRIB_File_List[1]
            grb_2 = None
            grb_3 = None
            grb_4 = None
            grb_5 = None
        
        if count == 2:
            grb_1 = GRIB_File_List[1]
            grb_2 = GRIB_File_List[2]
            grb_3 = None
            grb_4 = None
            grb_5 = None
            
        if count == 3: 
            grb_1 = GRIB_File_List[1]
            grb_2 = GRIB_File_List[2]
            grb_3 = GRIB_File_List[3]
            grb_4 = None
            grb_5 = None
        
        if count == 4: 
            grb_1 = GRIB_File_List[1]
            grb_2 = GRIB_File_List[2]
            grb_3 = GRIB_File_List[3]
            grb_4 = GRIB_File_List[4]
            grb_5 = None
    
        if count >= 5: 
            grb_1 = GRIB_File_List[1]
            grb_2 = GRIB_File_List[2]
            grb_3 = GRIB_File_List[3]
            grb_4 = GRIB_File_List[4]
            grb_5 = GRIB_File_List[5]
    
        print("There are " + str(count) + " GRIB files in the " + parameter + " download.")
        return grb_1, grb_2, grb_3, grb_4, grb_5, count
    
    
    def parse_GRIB_files(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files, grid_time_interval, parameter):
    
        r'''
        THIS FUNCTION PARSES THROUGH EACH GRIB FILE AND RETURNS THE VALUES OF THE FILE, THE START AND END TIME FOR THE FORECAST VALIDITY, THE LATITUDE AND LONGITUDE COORDINATES CORRESPONDING TO THE VALUES IN THE FILE. 
    
        (C) METEOROLOGIST ERIC J. DREWITZ 2023
    
        '''
    
        
        files = count_of_GRIB_files
        param = parameter
    
        if param == 'ds.mint.bin' or param == 'ds.maxt.bin':
            
            grb_1_vals, grb_2_vals, grb_3_vals, grb_4_vals, grb_5_vals = NDFD.GRIB_temperature_conversion(first_GRIB_file, second_GRIB_file, third_GRIB_file, fourth_GRIB_file, fifth_GRIB_file, count_of_GRIB_files)
            if files == 1:
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_start = None
                grb_2_end = None
                grb_3_start = None
                grb_3_end = None
                grb_4_start = None
                grb_4_end = None
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = None, None
                lats_3, lons_3 = None, None
                lats_4, lons_4 = None, None
                lats_5, lons_5 = None, None
        
            if files == 2:
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_start = None
                grb_3_end = None
                grb_4_start = None
                grb_4_end = None
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = None, None
                lats_4, lons_4 = None, None
                lats_5, lons_5 = None, None
        
            if files == 3:
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_start = third_GRIB_file.validDate
                grb_3_end = grb_3_start + timedelta(hours=grid_time_interval)
                grb_4_start = None
                grb_4_end = None
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = third_GRIB_file.latlons()
                lats_4, lons_4 = None, None
                lats_5, lons_5 = None, None
        
            if files == 4:
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_start = third_GRIB_file.validDate
                grb_3_end = grb_3_start + timedelta(hours=grid_time_interval)
                grb_4_start = fourth_GRIB_file.validDate
                grb_4_end = grb_4_start + timedelta(hours=grid_time_interval)
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = third_GRIB_file.latlons()
                lats_4, lons_4 = fourth_GRIB_file.latlons()
                lats_5, lons_5 = None, None
            
            
            if files >= 5:
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_start = third_GRIB_file.validDate
                grb_3_end = grb_3_start + timedelta(hours=grid_time_interval)
                grb_4_start = fourth_GRIB_file.validDate
                grb_4_end = grb_4_start + timedelta(hours=grid_time_interval)
                grb_5_start = fifth_GRIB_file.validDate
                grb_5_end = grb_5_start + timedelta(hours=grid_time_interval)
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = third_GRIB_file.latlons()
                lats_4, lons_4 = fourth_GRIB_file.latlons()
                lats_5, lons_5 = fifth_GRIB_file.latlons()
            
        
    
        else:       
       
            if files == 1:
                grb_1_vals = first_GRIB_file.values
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_vals = None
                grb_2_start = None
                grb_2_end = None
                grb_3_vals = None
                grb_3_start = None
                grb_3_end = None
                grb_4_vals = None
                grb_4_start = None
                grb_4_end = None
                grb_5_vals = None
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = None, None
                lats_3, lons_3 = None, None
                lats_4, lons_4 = None, None
                lats_5, lons_5 = None, None
        
            if files == 2:
                grb_1_vals = first_GRIB_file.values
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_vals = second_GRIB_file.values
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_vals = None
                grb_3_start = None
                grb_3_end = None
                grb_4_vals = None
                grb_4_start = None
                grb_4_end = None
                grb_5_vals = None
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = None, None
                lats_4, lons_4 = None, None
                lats_5, lons_5 = None, None
        
            if files == 3:
                grb_1_vals = first_GRIB_file.values
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_vals = second_GRIB_file.values
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_vals = third_GRIB_file.values
                grb_3_start = third_GRIB_file.validDate
                grb_3_end = grb_3_start + timedelta(hours=grid_time_interval)
                grb_4_vals = None
                grb_4_start = None
                grb_4_end = None
                grb_5_vals = None
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = third_GRIB_file.latlons()
                lats_4, lons_4 = None, None
                lats_5, lons_5 = None, None
        
            if files == 4:
                grb_1_vals = first_GRIB_file.values
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_vals = second_GRIB_file.values
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_vals = third_GRIB_file.values
                grb_3_start = third_GRIB_file.validDate
                grb_3_end = grb_3_start + timedelta(hours=grid_time_interval)
                grb_4_vals = fourth_GRIB_file.values
                grb_4_start = fourth_GRIB_file.validDate
                grb_4_end = grb_4_start + timedelta(hours=grid_time_interval)
                grb_5_vals = None
                grb_5_start = None
                grb_5_end = None
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = third_GRIB_file.latlons()
                lats_4, lons_4 = fourth_GRIB_file.latlons()
                lats_5, lons_5 = None, None
            
            
            if files >= 5:
                grb_1_vals = first_GRIB_file.values
                grb_1_start = first_GRIB_file.validDate
                grb_1_end = grb_1_start + timedelta(hours=grid_time_interval)
                grb_2_vals = second_GRIB_file.values
                grb_2_start = second_GRIB_file.validDate
                grb_2_end = grb_2_start + timedelta(hours=grid_time_interval)
                grb_3_vals = third_GRIB_file.values
                grb_3_start = third_GRIB_file.validDate
                grb_3_end = grb_3_start + timedelta(hours=grid_time_interval)
                grb_4_vals = fourth_GRIB_file.values
                grb_4_start = fourth_GRIB_file.validDate
                grb_4_end = grb_4_start + timedelta(hours=grid_time_interval)
                grb_5_vals = fifth_GRIB_file.values
                grb_5_start = fifth_GRIB_file.validDate
                grb_5_end = grb_5_start + timedelta(hours=grid_time_interval)
                          
                lats_1, lons_1 = first_GRIB_file.latlons()
                lats_2, lons_2 = second_GRIB_file.latlons()
                lats_3, lons_3 = third_GRIB_file.latlons()
                lats_4, lons_4 = fourth_GRIB_file.latlons()
                lats_5, lons_5 = fifth_GRIB_file.latlons()
    
    
        return grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5
    
    def GRIB_file_checker(GRIB_File_List):
        
        r'''
        THIS FUNCTION IS USEFUL WHEN HAVING AUTOMATED DISPLAYS OF THE VARIOUS GRIB FILE DATA
    
        THIS FUNCTION CHECKS TO SEE HOW MANY GRIB FILES ARE RETURNED IN THE LIST WHICH IS HELPFUL FOR GRAPHICS
    
        THIS FUNCTION IS TO BE USED IN THE PROGRAMMER'S CODE AFTER THE get_NWS_NDFD_grid_data(directory_name, parameter) FUNCTION IS USED
    
        THIS FUNCTION WILL RETURN A BOOLEAN VALUE FOR IF OR IF NOT THE FILE EXISTS
    
        USUALLY THERE ARE NOT MORE THAN 5 GRIB FILES IN A DOWNLOAD AT A TIME
    
        IF THE GRIB FILE EXISTS, A BOOLEAN VALUE OF TRUE IS RETURNED AND IF THE GRIB FILE DOESN'T EXIST A BOOLEAN VALUE OF FALSE IS RETURNED. 
    
        THE LOGICAL CHECKS HELPS WHEN THE USER IS MAKING AUTOMATED GRAPHICS TO MAKE SURE THE NUMBER OF SUBPLOTS IS EQUAL TO THE NUMBER OF GRIB FILES
    
        THIS FUNCTION ALSO RETURNS THE COUNT OF THE NUMBER OF GRIB FILES IN THE DATASET.
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
        count = 0
        for grb in GRIB_File_List:
            count = count + 1
        if count == 1:
            grb_1_logic = True
            grb_2_logic = False
            grb_3_logic = False
            grb_4_logic = False
            grb_5_logic = False
        
        if count == 2:
            grb_1_logic = True
            grb_2_logic = True
            grb_3_logic = False
            grb_4_logic = False
            grb_5_logic = False
            
        if count == 3: 
            grb_1_logic = True
            grb_2_logic = True
            grb_3_logic = True
            grb_4_logic = False
            grb_5_logic = False
        
        if count == 4: 
            grb_1_logic = True
            grb_2_logic = True
            grb_3_logic = True
            grb_4_logic = True
            grb_5_logic = False
    
        if count >= 5: 
            grb_1_logic = True
            grb_2_logic = True
            grb_3_logic = True
            grb_4_logic = True
            grb_5_logic = True
    
        return grb_1_logic, grb_2_logic, grb_3_logic, grb_4_logic, grb_5_logic, count
    
    
    
    def get_GRIB_file_values(GRIB_File):
     
        r'''
        THIS FUNCTION RETURNS THE VALUES OF THE DATA INSIDE OF A GRIB FILE. 
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
        return GRIB_File.values
    
    
    def get_GRIB_file_valid_date(GRIB_File):
    
        r'''
        THIS FUNCTION RETURNS THE VALID DATE FOR A GRIB FILE
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
        return GRIB_File.validDate
    
    
    def NDFD_Forecast_Time_Interval(GRIB_File, hours): 
       
        r'''
        THIS FUNCTION WILL RETURN THE TIME THE FORECAST PERIOD ENDS BASED ON HOW LONG THE FORECAST PERIOD IS VALID FOR
        THE VALID DATE FOR A GRIB FILE CORRESPONDS TO THE START OF THE FORECAST PERIOD. 
        (I.E. THE NDFD MAXIMUM RELATIVE HUMIDITY GRIDS ARE A TIME LENGTH OF 12HRS, THEREFORE THE ENDING TIME OF THE FORECAST PERIOD IS 12HRS AFTER THE VALID DATE OF THE GRIB FILE. 
    
        PYTHON MODULE DEPENDENCIES:
        1. DATETIME
    
        COPYRIGHT (C) METEOROLOGIST ERIC J. DREWITZ 2023
        '''
    
        return GRIB_File.validDate + timedelta(hours=hours)

class checks:

    r'''

    THIS CLASS HOSTS FUNCTIONS TO CHECK TO MAKE SURE WE ARE COMPARING DATASETS FOR THE SAME TIME

    '''

    def check_RTMA_vs_METAR_Times(real_time_mesoscale_analysis_time, metar_observation_time):

        r'''
        THIS FUNCTION MAKES SURE THE TIMES MATCH BETWEEN THE RTMA DATA AND METAR DATA. A LOT OF TIMES, THE METAR DATA IS 1-2 HOURS AHEAD OF THE RTMA DATA. THE FUNCTION RETURNS THE TIME OF THE LATEST RTMA DATASET TO USE AS THE TIME WHEN QUERYING THE METAR DATASETS

        (C) METEOROLOGIST ERIC J. DREWITZ

        '''

        metar_time = metar_observation_time

        rtma_time = real_time_mesoscale_analysis_time

        time_diff = metar_time.hour - rtma_time.hour

        if metar_time.hour > rtma_time.hour:
            new_metar_time = metar_time - timedelta(hours=time_diff)

        if metar_time.hour < rtma_time.hour:
            hour = rtma_time.hour
            new_metar_time = metar_time - timedelta(days=1)
            year = new_metar_time.year
            month = new_metar_time.month
            day = new_metar_time.day
            new_metar_time = datetime(year, month, day, hour)

        else:
            new_metar_time = rtma_time
            

        return new_metar_time
