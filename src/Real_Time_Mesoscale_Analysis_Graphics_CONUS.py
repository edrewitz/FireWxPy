'''
This file hosts all the Real Time Mesoscale Analysis (RTMA) plotting functions in FireWxPy for CONUS aka the "Lower-48". 
The RTMA data consists of gridded data for current conditions with a grid spacing of 2.5km x 2.5km.

There are 2 classes which are used to define the perspective of the plot: 
1) Counties_Perspective - This class uses state and county borders as the geographical reference. 
2) Predictive_Services_Areas_Perspective - This class uses the Geographic Area Coordination Center (GACC) and Predictive Services Area (PSA) boundaries as the geographical reference. 

This file was written by Meteorologist Eric J. Drewitz 

            (C) Meteorologist Eric J. Drewitz 
                        USDA/USFS
'''

import pytz
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import metpy.plots as mpplots
import metpy.calc as mpcalc
import numpy as np
import parsers
import data_access as da
import geometry
import calc
import colormaps
import pandas as pd
import matplotlib.gridspec as gridspec

from matplotlib.patheffects import withStroke
from metpy.plots import USCOUNTIES
from datetime import datetime, timedelta
from metpy.plots import colortables
from NWS_Generic_Forecast_Graphics import standard
from dateutil import tz

class Counties_Perspective:

    r'''
    This class hosts the graphics using county and state boundaries as the geographic reference
    '''
    def plot_generic_real_time_mesoanalysis_no_METARs(parameter, plot_title, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table, color_table_title, color_table_start, color_table_stop, color_table_step, color_table_shrink, state_border_color, state_border_line_thickness, county_border_color, county_border_line_thickness, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''

            This function does the following:
                                            1) Downloads the data that corresponds to the parameter the user requests. 
                                            2) Converts the units of the data (if needed).
                                            3) Plots the data that corresponds to the parameter the user requests. 

            

            Inputs:
                1) parameter (String) - The parameter the user chooses to plot. For the full parameter list, visit: https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/NDFD/NWS/CONUS/CONDUIT/Best.html

                2) plot_title (String) - The title of the entire figure. 

                3) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                4) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                5) color_table (String) - The color table used for the scale of the data being plotted. See either the FireWxPy and/or matplotlib colortable documentation for colortable options. 

                6) color_table_title (String) - The title along the colorbar on the edge of the figure. 

                7) color_table_start (Integer) - The bottom bound of the color scale reference used to plot the data. 

                8) color_table_stop (Integer) - The top bound of the color scale reference used to plot the data.

                9) color_table_step (Integer) - The increment of the color scale (i.e. every 1 degree vs. every 5 degrees). 

                10) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                11) state_border_color (String) - Color of the state border. 

                12) state_border_line_thickness (Integer or Float) - Thickness of the state border lines. 

                13) county_border_color (String) - Color of the county border. 

                14) county_border_line_thickness (Integer or Float) - Thickness of the county border lines.

                15) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                16) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                17) title_font_size (Integer) - The fontsize of the title of the figure. 

                18) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                19) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                20) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                21) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the parameter the user wishes to plot. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()
        param = parameter

        if param == 'Wind_speed_gust_Analysis_height_above_ground' or param == 'Wind_speed_Analysis_height_above_ground' or param == 'Wind_speed_error_height_above_ground' or param == 'Wind_speed_gust_error_height_above_ground' or param == 'u-component_of_wind_Analysis_height_above_ground' or param == 'v-component_of_wind_Analysis_height_above_ground':

            data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, param)
            data = data * 2.23694

        if param == 'Temperature_Analysis_height_above_ground' or param == 'Dewpoint_temperature_Analysis_height_above_ground' or param == 'Temperature_error_height_above_ground' or param == 'Dewpoint_temperature_error_height_above_ground':
            
            data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, param)
            data = calc.unit_conversion.RTMA_Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(data)
            

        else:
            data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, param)
            
        plot_proj = data.metpy.cartopy_crs

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_line_thickness, edgecolor=state_border_color, zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_line_thickness, edgecolor=county_border_color, zorder=4)

        cs = ax.contourf(data.metpy.x, data.metpy.y, data, 
                         transform=data.metpy.cartopy_crs, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, alpha=0.5)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label=color_table_title, size=colorbar_label_font_size, fontweight='bold')

        plt.title(plot_title + "\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_generic_real_time_mesoanalysis_with_METARs(parameter, plot_title, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table, color_table_title, color_table_start, color_table_stop, color_table_step, color_table_shrink, mask, state_border_color, state_border_line_thickness, county_border_color, county_border_line_thickness, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the data that corresponds to the parameter the user requests. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Converts the units of the data (if needed).
                                            4) Plots the data that corresponds to the parameter the user requests. 

            

            Inputs:
                1) parameter (String) - The parameter the user chooses to plot. For the full parameter list, visit: https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/NDFD/NWS/CONUS/CONDUIT/Best.html

                2) plot_title (String) - The title of the entire figure. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) color_table (String) - The color table used for the scale of the data being plotted. See either the FireWxPy and/or matplotlib colortable documentation for colortable options. 

                14) color_table_title (String) - The title along the colorbar on the edge of the figure. 

                15) color_table_start (Integer) - The bottom bound of the color scale reference used to plot the data. 

                16) color_table_stop (Integer) - The top bound of the color scale reference used to plot the data.

                17) color_table_step (Integer) - The increment of the color scale (i.e. every 1 degree vs. every 5 degrees). 

                18) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                19) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 
          
                19) state_border_color (String) - Color of the state border. 

                20) state_border_line_thickness (Integer or Float) - Thickness of the state border lines. 

                21) county_border_color (String) - Color of the county border. 

                22) county_border_line_thickness (Integer or Float) - Thickness of the county border lines.

                23) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                24) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                25) title_font_size (Integer) - The fontsize of the title of the figure. 

                26) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                27) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                28) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                29) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the parameter the user wishes to plot plus the METAR plots for the same time as the Real Time Mesoscale Analysis. 
        
        
        '''


        local_time, utc_time = standard.plot_creation_time()
        param = parameter

        if param == 'Wind_speed_gust_Analysis_height_above_ground' or param == 'Wind_speed_Analysis_height_above_ground' or param == 'Wind_speed_error_height_above_ground' or param == 'Wind_speed_gust_error_height_above_ground' or param == 'u-component_of_wind_Analysis_height_above_ground' or param == 'v-component_of_wind_Analysis_height_above_ground':

           rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Synced_With_METAR(param, utc_time, mask)
           rtma_data = rtma_data * 2.23694

        if param == 'Temperature_Analysis_height_above_ground' or param == 'Dewpoint_temperature_Analysis_height_above_ground' or param == 'Temperature_error_height_above_ground' or param == 'Dewpoint_temperature_error_height_above_ground':
            
            rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Synced_With_METAR(param, utc_time, mask)
            rtma_data = calc.unit_conversion.RTMA_Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(rtma_data)
            

        else:
           rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Synced_With_METAR(param, utc_time, mask)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        metar_time_revised = metar_time_revised.astimezone(to_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_line_thickness, edgecolor=state_border_color, zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_line_thickness, edgecolor=county_border_color, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, alpha=0.5)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label=color_table_title, size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn = mpplots.StationPlot(ax, sfc_data['longitude'][sfc_data_mask].m, sfc_data['latitude'][sfc_data_mask].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn.plot_parameter('NW', sfc_data['air_temperature'].to('degF')[sfc_data_mask], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_parameter('SW', sfc_data['dew_point_temperature'].to('degF')[sfc_data_mask], color='blue',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_symbol('C', sfc_data['cloud_coverage'][sfc_data_mask], mpplots.sky_cover)
        
        stn.plot_parameter('E', sfc_data_rh.to('percent')[sfc_data_mask], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_barb(sfc_data['u'][sfc_data_mask], sfc_data['v'][sfc_data_mask])

        plt.title(plot_title + "\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised.strftime('%m/%d/%Y %H:00 Local'), fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig



    def plot_relative_humidity_with_METARs(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, mask, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the relative humidity data overlayed with the METAR reports. 

            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(utc_time, mask)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        metar_time_revised = metar_time_revised.replace(tzinfo=from_zone)
        metar_time_revised = metar_time_revised.astimezone(to_zone)
        metar_time_revised_utc = metar_time_revised.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        cmap = colormaps.relative_humidity_colormap()

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn = mpplots.StationPlot(ax, sfc_data['longitude'][sfc_data_mask].m, sfc_data['latitude'][sfc_data_mask].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn.plot_parameter('NW', sfc_data['air_temperature'].to('degF')[sfc_data_mask], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_parameter('SW', sfc_data['dew_point_temperature'].to('degF')[sfc_data_mask], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_symbol('C', sfc_data['cloud_coverage'][sfc_data_mask], mpplots.sky_cover)
        
        stn.plot_parameter('E', sfc_data_rh.to('percent')[sfc_data_mask], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_barb(sfc_data['u'][sfc_data_mask], sfc_data['v'][sfc_data_mask])

        plt.title("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_relative_humidity_with_METARs_6hr_timelapse(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, mask, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the relative humidity data overlayed with the METAR reports. 

            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        times = []

        for i in range(0, 10):
            time = utc_time - timedelta(hours=i)
            times.append(time)

        t1 = times[0]
        t2 = times[1]
        t3 = times[2]
        t4 = times[3]
        t5 = times[4]
        t6 = times[5]
        t7 = times[6]
        t8 = times[7]
        t9 = times[8]
        t10 = times[9]

        rtma_data_0, rtma_time_0, sfc_data_0, sfc_data_u_kt_0, sfc_data_v_kt_0, sfc_data_rh_0, sfc_data_mask_0, metar_time_revised_0, plot_proj_0 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t1, mask)

        rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t2, mask)

        if rtma_time_0.hour == rtma_time_1.hour:

            rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t3, mask)

            if rtma_time_0.hour == rtma_time_1.hour:

                rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t4, mask)

                rtma_data_2, rtma_time_2, sfc_data_2, sfc_data_u_kt_2, sfc_data_v_kt_2, sfc_data_rh_2, sfc_data_mask_2, metar_time_revised_2, plot_proj_2 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t5, mask)
        
                rtma_data_3, rtma_time_3, sfc_data_3, sfc_data_u_kt_3, sfc_data_v_kt_3, sfc_data_rh_3, sfc_data_mask_3, metar_time_revised_3, plot_proj_3 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t6, mask)
        
                rtma_data_4, rtma_time_4, sfc_data_4, sfc_data_u_kt_4, sfc_data_v_kt_4, sfc_data_rh_4, sfc_data_mask_4, metar_time_revised_4, plot_proj_4 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t7, mask)
        
                rtma_data_5, rtma_time_5, sfc_data_5, sfc_data_u_kt_5, sfc_data_v_kt_5, sfc_data_rh_5, sfc_data_mask_5, metar_time_revised_5, plot_proj_5 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t8, mask)
        
                rtma_data_6, rtma_time_6, sfc_data_6, sfc_data_u_kt_6, sfc_data_v_kt_6, sfc_data_rh_6, sfc_data_mask_6, metar_time_revised_6, plot_proj_6 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t9, mask)

            else:

                rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t3, mask)
                
                rtma_data_2, rtma_time_2, sfc_data_2, sfc_data_u_kt_2, sfc_data_v_kt_2, sfc_data_rh_2, sfc_data_mask_2, metar_time_revised_2, plot_proj_2 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t4, mask)
        
                rtma_data_3, rtma_time_3, sfc_data_3, sfc_data_u_kt_3, sfc_data_v_kt_3, sfc_data_rh_3, sfc_data_mask_3, metar_time_revised_3, plot_proj_3 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t5, mask)
        
                rtma_data_4, rtma_time_4, sfc_data_4, sfc_data_u_kt_4, sfc_data_v_kt_4, sfc_data_rh_4, sfc_data_mask_4, metar_time_revised_4, plot_proj_4 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t6, mask)
        
                rtma_data_5, rtma_time_5, sfc_data_5, sfc_data_u_kt_5, sfc_data_v_kt_5, sfc_data_rh_5, sfc_data_mask_5, metar_time_revised_5, plot_proj_5 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t7, mask)
        
                rtma_data_6, rtma_time_6, sfc_data_6, sfc_data_u_kt_6, sfc_data_v_kt_6, sfc_data_rh_6, sfc_data_mask_6, metar_time_revised_6, plot_proj_6 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t8, mask)

        else:

            rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t2, mask)

            rtma_data_2, rtma_time_2, sfc_data_2, sfc_data_u_kt_2, sfc_data_v_kt_2, sfc_data_rh_2, sfc_data_mask_2, metar_time_revised_2, plot_proj_2 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t3, mask)
    
            rtma_data_3, rtma_time_3, sfc_data_3, sfc_data_u_kt_3, sfc_data_v_kt_3, sfc_data_rh_3, sfc_data_mask_3, metar_time_revised_3, plot_proj_3 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t4, mask)
    
            rtma_data_4, rtma_time_4, sfc_data_4, sfc_data_u_kt_4, sfc_data_v_kt_4, sfc_data_rh_4, sfc_data_mask_4, metar_time_revised_4, plot_proj_4 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t5, mask)
    
            rtma_data_5, rtma_time_5, sfc_data_5, sfc_data_u_kt_5, sfc_data_v_kt_5, sfc_data_rh_5, sfc_data_mask_5, metar_time_revised_5, plot_proj_5 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t6, mask)
    
            rtma_data_6, rtma_time_6, sfc_data_6, sfc_data_u_kt_6, sfc_data_v_kt_6, sfc_data_rh_6, sfc_data_mask_6, metar_time_revised_6, plot_proj_6 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t7, mask)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        
        rtma_time_0 = rtma_time_0.replace(tzinfo=from_zone)
        rtma_time_0 = rtma_time_0.astimezone(to_zone)
        rtma_time_utc_0 = rtma_time_0.astimezone(from_zone)
        metar_time_revised_0 = metar_time_revised_0.replace(tzinfo=from_zone)
        metar_time_revised_0 = metar_time_revised_0.astimezone(to_zone)
        metar_time_revised_0_utc = metar_time_revised_0.astimezone(from_zone)

        rtma_time_1 = rtma_time_1.replace(tzinfo=from_zone)
        rtma_time_1 = rtma_time_1.astimezone(to_zone)
        rtma_time_utc_1 = rtma_time_1.astimezone(from_zone)
        metar_time_revised_1 = metar_time_revised_1.replace(tzinfo=from_zone)
        metar_time_revised_1 = metar_time_revised_1.astimezone(to_zone)
        metar_time_revised_1_utc = metar_time_revised_1.astimezone(from_zone)

        rtma_time_2 = rtma_time_2.replace(tzinfo=from_zone)
        rtma_time_2 = rtma_time_2.astimezone(to_zone)
        rtma_time_utc_2 = rtma_time_2.astimezone(from_zone)
        metar_time_revised_2 = metar_time_revised_2.replace(tzinfo=from_zone)
        metar_time_revised_2 = metar_time_revised_2.astimezone(to_zone)
        metar_time_revised_2_utc = metar_time_revised_2.astimezone(from_zone)

        rtma_time_3 = rtma_time_3.replace(tzinfo=from_zone)
        rtma_time_3 = rtma_time_3.astimezone(to_zone)
        rtma_time_utc_3 = rtma_time_3.astimezone(from_zone)
        metar_time_revised_3 = metar_time_revised_3.replace(tzinfo=from_zone)
        metar_time_revised_3 = metar_time_revised_3.astimezone(to_zone)
        metar_time_revised_3_utc = metar_time_revised_3.astimezone(from_zone)

        rtma_time_4 = rtma_time_4.replace(tzinfo=from_zone)
        rtma_time_4 = rtma_time_4.astimezone(to_zone)
        rtma_time_utc_4 = rtma_time_4.astimezone(from_zone)
        metar_time_revised_4 = metar_time_revised_4.replace(tzinfo=from_zone)
        metar_time_revised_4 = metar_time_revised_4.astimezone(to_zone)
        metar_time_revised_4_utc = metar_time_revised_4.astimezone(from_zone)

        rtma_time_5 = rtma_time_5.replace(tzinfo=from_zone)
        rtma_time_5 = rtma_time_5.astimezone(to_zone)
        rtma_time_utc_5 = rtma_time_5.astimezone(from_zone)
        metar_time_revised_5 = metar_time_revised_5.replace(tzinfo=from_zone)
        metar_time_revised_5 = metar_time_revised_5.astimezone(to_zone)
        metar_time_revised_5_utc = metar_time_revised_5.astimezone(from_zone)

        rtma_time_6 = rtma_time_6.replace(tzinfo=from_zone)
        rtma_time_6 = rtma_time_6.astimezone(to_zone)
        rtma_time_utc_6 = rtma_time_6.astimezone(from_zone)
        metar_time_revised_6 = metar_time_revised_6.replace(tzinfo=from_zone)
        metar_time_revised_6 = metar_time_revised_6.astimezone(to_zone)
        metar_time_revised_6_utc = metar_time_revised_6.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        cmap = colormaps.relative_humidity_colormap()

        figs = []

        ################
        # FIRST FIGURE #
        ################

        fig1 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig1.set_facecolor('aliceblue')

        ax1 = fig1.add_subplot(1, 1, 1, projection=plot_proj_0)
        ax1.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax1.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax1.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs1 = ax1.contourf(rtma_data_0.metpy.x, rtma_data_0.metpy.y, rtma_data_0, 
                         transform=rtma_data_0.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar1 = fig1.colorbar(cs1, shrink=color_table_shrink, pad=colorbar_pad)
        cbar1.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn1 = mpplots.StationPlot(ax1, sfc_data_0['longitude'][sfc_data_mask_0].m, sfc_data_0['latitude'][sfc_data_mask_0].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn1.plot_parameter('NW', sfc_data_0['air_temperature'].to('degF')[sfc_data_mask_0], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn1.plot_parameter('SW', sfc_data_0['dew_point_temperature'].to('degF')[sfc_data_mask_0], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn1.plot_symbol('C', sfc_data_0['cloud_coverage'][sfc_data_mask_0], mpplots.sky_cover)
        
        stn1.plot_parameter('E', sfc_data_rh_0.to('percent')[sfc_data_mask_0], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn1.plot_barb(sfc_data_0['u'][sfc_data_mask_0], sfc_data_0['v'][sfc_data_mask_0])

        fig1.suptitle("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time_0.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_0.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised_0.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_0_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax1.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax1.transAxes)

        #################
        # SECOND FIGURE #
        #################

        fig2 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig2.set_facecolor('aliceblue')

        ax2 = fig2.add_subplot(1, 1, 1, projection=plot_proj_1)
        ax2.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax2.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax2.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs2 = ax2.contourf(rtma_data_1.metpy.x, rtma_data_1.metpy.y, rtma_data_1, 
                         transform=rtma_data_1.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar2 = fig2.colorbar(cs2, shrink=color_table_shrink, pad=colorbar_pad)
        cbar2.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn2 = mpplots.StationPlot(ax2, sfc_data_1['longitude'][sfc_data_mask_1].m, sfc_data_1['latitude'][sfc_data_mask_1].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn2.plot_parameter('NW', sfc_data_1['air_temperature'].to('degF')[sfc_data_mask_1], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn2.plot_parameter('SW', sfc_data_1['dew_point_temperature'].to('degF')[sfc_data_mask_1], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn2.plot_symbol('C', sfc_data_1['cloud_coverage'][sfc_data_mask_1], mpplots.sky_cover)
        
        stn2.plot_parameter('E', sfc_data_rh_1.to('percent')[sfc_data_mask_1], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn2.plot_barb(sfc_data_1['u'][sfc_data_mask_1], sfc_data_1['v'][sfc_data_mask_1])

        fig2.suptitle("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time_1.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_1.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised_1.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_1_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax2.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax2.transAxes)

        ################
        # THIRD FIGURE #
        ################

        fig3 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig3.set_facecolor('aliceblue')

        ax3 = fig3.add_subplot(1, 1, 1, projection=plot_proj_2)
        ax3.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax3.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax3.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax3.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax3.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax3.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs3 = ax3.contourf(rtma_data_2.metpy.x, rtma_data_2.metpy.y, rtma_data_2, 
                         transform=rtma_data_2.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar3 = fig3.colorbar(cs3, shrink=color_table_shrink, pad=colorbar_pad)
        cbar3.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn3 = mpplots.StationPlot(ax3, sfc_data_2['longitude'][sfc_data_mask_2].m, sfc_data_2['latitude'][sfc_data_mask_2].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn3.plot_parameter('NW', sfc_data_2['air_temperature'].to('degF')[sfc_data_mask_2], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn3.plot_parameter('SW', sfc_data_2['dew_point_temperature'].to('degF')[sfc_data_mask_2], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn3.plot_symbol('C', sfc_data_2['cloud_coverage'][sfc_data_mask_2], mpplots.sky_cover)
        
        stn3.plot_parameter('E', sfc_data_rh_2.to('percent')[sfc_data_mask_2], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn3.plot_barb(sfc_data_2['u'][sfc_data_mask_2], sfc_data_2['v'][sfc_data_mask_2])

        fig3.suptitle("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time_2.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_2.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised_2.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_2_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax3.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax3.transAxes)


        #################
        # FOURTH FIGURE #
        #################

        fig4 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig4.set_facecolor('aliceblue')

        ax4 = fig4.add_subplot(1, 1, 1, projection=plot_proj_3)
        ax4.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax4.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax4.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax4.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax4.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax4.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax4.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax4.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs4 = ax4.contourf(rtma_data_3.metpy.x, rtma_data_3.metpy.y, rtma_data_3, 
                         transform=rtma_data_3.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar4 = fig4.colorbar(cs4, shrink=color_table_shrink, pad=colorbar_pad)
        cbar4.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn4 = mpplots.StationPlot(ax4, sfc_data_3['longitude'][sfc_data_mask_3].m, sfc_data_3['latitude'][sfc_data_mask_3].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn4.plot_parameter('NW', sfc_data_3['air_temperature'].to('degF')[sfc_data_mask_3], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn4.plot_parameter('SW', sfc_data_3['dew_point_temperature'].to('degF')[sfc_data_mask_3], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn4.plot_symbol('C', sfc_data_3['cloud_coverage'][sfc_data_mask_3], mpplots.sky_cover)
        
        stn4.plot_parameter('E', sfc_data_rh_3.to('percent')[sfc_data_mask_3], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn4.plot_barb(sfc_data_3['u'][sfc_data_mask_3], sfc_data_3['v'][sfc_data_mask_3])

        fig4.suptitle("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time_3.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_3.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised_3.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_3_utc.strftime('%H:00 Local')+")", fontsize=title_font_size, fontweight='bold')
        
        ax4.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax4.transAxes)


        ################
        # FIFTH FIGURE #
        ################

        fig5 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig5.set_facecolor('aliceblue')

        ax5 = fig5.add_subplot(1, 1, 1, projection=plot_proj_4)
        ax5.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax5.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax5.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax5.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax5.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax5.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax5.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax5.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs5 = ax5.contourf(rtma_data_4.metpy.x, rtma_data_4.metpy.y, rtma_data_4, 
                         transform=rtma_data_4.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar5 = fig5.colorbar(cs5, shrink=color_table_shrink, pad=colorbar_pad)
        cbar5.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn5 = mpplots.StationPlot(ax5, sfc_data_4['longitude'][sfc_data_mask_4].m, sfc_data_4['latitude'][sfc_data_mask_4].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn5.plot_parameter('NW', sfc_data_4['air_temperature'].to('degF')[sfc_data_mask_4], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn5.plot_parameter('SW', sfc_data_4['dew_point_temperature'].to('degF')[sfc_data_mask_4], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn5.plot_symbol('C', sfc_data_4['cloud_coverage'][sfc_data_mask_4], mpplots.sky_cover)
        
        stn5.plot_parameter('E', sfc_data_rh_4.to('percent')[sfc_data_mask_4], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn5.plot_barb(sfc_data_4['u'][sfc_data_mask_4], sfc_data_4['v'][sfc_data_mask_4])

        fig5.suptitle("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time_4.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_4.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised_4.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_4_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax5.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax5.transAxes)

        ################
        # SIXTH FIGURE #
        ################

        fig6 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig6.set_facecolor('aliceblue')

        ax6 = fig6.add_subplot(1, 1, 1, projection=plot_proj_5)
        ax6.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax6.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax6.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax6.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax6.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax6.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax6.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax6.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs6 = ax6.contourf(rtma_data_5.metpy.x, rtma_data_5.metpy.y, rtma_data_5, 
                         transform=rtma_data_5.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar6 = fig6.colorbar(cs6, shrink=color_table_shrink, pad=colorbar_pad)
        cbar6.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn6 = mpplots.StationPlot(ax6, sfc_data_5['longitude'][sfc_data_mask_5].m, sfc_data_5['latitude'][sfc_data_mask_5].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn6.plot_parameter('NW', sfc_data_5['air_temperature'].to('degF')[sfc_data_mask_5], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn6.plot_parameter('SW', sfc_data_5['dew_point_temperature'].to('degF')[sfc_data_mask_5], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn6.plot_symbol('C', sfc_data_5['cloud_coverage'][sfc_data_mask_5], mpplots.sky_cover)
        
        stn6.plot_parameter('E', sfc_data_rh_5.to('percent')[sfc_data_mask_5], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn6.plot_barb(sfc_data_5['u'][sfc_data_mask_5], sfc_data_5['v'][sfc_data_mask_5])

        fig6.suptitle("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time_5.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_5.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised_5.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_5_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax6.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax6.transAxes)

        ##################
        # SEVENTH FIGURE #
        ##################

        fig7 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig7.set_facecolor('aliceblue')

        ax7 = fig7.add_subplot(1, 1, 1, projection=plot_proj_6)
        ax7.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax7.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax7.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax7.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax7.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax7.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax7.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax7.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs7 = ax7.contourf(rtma_data_6.metpy.x, rtma_data_6.metpy.y, rtma_data_6, 
                         transform=rtma_data_6.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar7 = fig7.colorbar(cs7, shrink=color_table_shrink, pad=colorbar_pad)
        cbar7.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn7 = mpplots.StationPlot(ax7, sfc_data_6['longitude'][sfc_data_mask_6].m, sfc_data_6['latitude'][sfc_data_mask_6].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn7.plot_parameter('NW', sfc_data_6['air_temperature'].to('degF')[sfc_data_mask_6], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn7.plot_parameter('SW', sfc_data_6['dew_point_temperature'].to('degF')[sfc_data_mask_6], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn7.plot_symbol('C', sfc_data_6['cloud_coverage'][sfc_data_mask_6], mpplots.sky_cover)
        
        stn7.plot_parameter('E', sfc_data_rh_6.to('percent')[sfc_data_mask_6], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn7.plot_barb(sfc_data_6['u'][sfc_data_mask_6], sfc_data_6['v'][sfc_data_mask_6])

        fig7.suptitle("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time_6.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc_6.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised_6.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_6_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax7.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax7.transAxes)

        figs.append(fig7)
        figs.append(fig6)
        figs.append(fig5)
        figs.append(fig4)
        figs.append(fig3)
        figs.append(fig2)
        figs.append(fig1)

        return figs



    def plot_relative_humidity_and_trend_with_METARs_6hr_timelapse(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, mask, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the relative humidity data overlayed with the METAR reports. 

            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        times = []

        for i in range(0, 10):
            time = utc_time - timedelta(hours=i)
            times.append(time)

        t1 = times[0]
        t2 = times[1]
        t3 = times[2]
        t4 = times[3]
        t5 = times[4]
        t6 = times[5]
        t7 = times[6]
        t8 = times[7]
        t9 = times[8]
        t10 = times[9]

        rtma_data_0, rtma_time_0, sfc_data_0, sfc_data_u_kt_0, sfc_data_v_kt_0, sfc_data_rh_0, sfc_data_mask_0, metar_time_revised_0, plot_proj_0 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t1, mask)

        rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t2, mask)

        if rtma_time_0.hour == rtma_time_1.hour:

            rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t3, mask)

            if rtma_time_0.hour == rtma_time_1.hour:

                rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t4, mask)

                rtma_data_2, rtma_time_2, sfc_data_2, sfc_data_u_kt_2, sfc_data_v_kt_2, sfc_data_rh_2, sfc_data_mask_2, metar_time_revised_2, plot_proj_2 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t5, mask)
        
                rtma_data_3, rtma_time_3, sfc_data_3, sfc_data_u_kt_3, sfc_data_v_kt_3, sfc_data_rh_3, sfc_data_mask_3, metar_time_revised_3, plot_proj_3 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t6, mask)
        
                rtma_data_4, rtma_time_4, sfc_data_4, sfc_data_u_kt_4, sfc_data_v_kt_4, sfc_data_rh_4, sfc_data_mask_4, metar_time_revised_4, plot_proj_4 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t7, mask)
        
                rtma_data_5, rtma_time_5, sfc_data_5, sfc_data_u_kt_5, sfc_data_v_kt_5, sfc_data_rh_5, sfc_data_mask_5, metar_time_revised_5, plot_proj_5 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t8, mask)
        
                rtma_data_6, rtma_time_6, sfc_data_6, sfc_data_u_kt_6, sfc_data_v_kt_6, sfc_data_rh_6, sfc_data_mask_6, metar_time_revised_6, plot_proj_6 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t9, mask)

                rtma_data_7, rtma_time_7, sfc_data_7, sfc_data_u_kt_7, sfc_data_v_kt_7, sfc_data_rh_7, sfc_data_mask_7, metar_time_revised_7, plot_proj_7 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t10, mask)


            else:

                rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t3, mask)
                
                rtma_data_2, rtma_time_2, sfc_data_2, sfc_data_u_kt_2, sfc_data_v_kt_2, sfc_data_rh_2, sfc_data_mask_2, metar_time_revised_2, plot_proj_2 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t4, mask)
        
                rtma_data_3, rtma_time_3, sfc_data_3, sfc_data_u_kt_3, sfc_data_v_kt_3, sfc_data_rh_3, sfc_data_mask_3, metar_time_revised_3, plot_proj_3 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t5, mask)
        
                rtma_data_4, rtma_time_4, sfc_data_4, sfc_data_u_kt_4, sfc_data_v_kt_4, sfc_data_rh_4, sfc_data_mask_4, metar_time_revised_4, plot_proj_4 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t6, mask)
        
                rtma_data_5, rtma_time_5, sfc_data_5, sfc_data_u_kt_5, sfc_data_v_kt_5, sfc_data_rh_5, sfc_data_mask_5, metar_time_revised_5, plot_proj_5 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t7, mask)
        
                rtma_data_6, rtma_time_6, sfc_data_6, sfc_data_u_kt_6, sfc_data_v_kt_6, sfc_data_rh_6, sfc_data_mask_6, metar_time_revised_6, plot_proj_6 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t8, mask)

                rtma_data_7, rtma_time_7, sfc_data_7, sfc_data_u_kt_7, sfc_data_v_kt_7, sfc_data_rh_7, sfc_data_mask_7, metar_time_revised_7, plot_proj_7 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t9, mask)

        else:

            rtma_data_1, rtma_time_1, sfc_data_1, sfc_data_u_kt_1, sfc_data_v_kt_1, sfc_data_rh_1, sfc_data_mask_1, metar_time_revised_1, plot_proj_1 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t2, mask)

            rtma_data_2, rtma_time_2, sfc_data_2, sfc_data_u_kt_2, sfc_data_v_kt_2, sfc_data_rh_2, sfc_data_mask_2, metar_time_revised_2, plot_proj_2 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t3, mask)
    
            rtma_data_3, rtma_time_3, sfc_data_3, sfc_data_u_kt_3, sfc_data_v_kt_3, sfc_data_rh_3, sfc_data_mask_3, metar_time_revised_3, plot_proj_3 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t4, mask)
    
            rtma_data_4, rtma_time_4, sfc_data_4, sfc_data_u_kt_4, sfc_data_v_kt_4, sfc_data_rh_4, sfc_data_mask_4, metar_time_revised_4, plot_proj_4 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t5, mask)
    
            rtma_data_5, rtma_time_5, sfc_data_5, sfc_data_u_kt_5, sfc_data_v_kt_5, sfc_data_rh_5, sfc_data_mask_5, metar_time_revised_5, plot_proj_5 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t6, mask)
    
            rtma_data_6, rtma_time_6, sfc_data_6, sfc_data_u_kt_6, sfc_data_v_kt_6, sfc_data_rh_6, sfc_data_mask_6, metar_time_revised_6, plot_proj_6 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t7, mask)

            rtma_data_7, rtma_time_7, sfc_data_7, sfc_data_u_kt_7, sfc_data_v_kt_7, sfc_data_rh_7, sfc_data_mask_7, metar_time_revised_7, plot_proj_7 = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(t8, mask)

        diff1 = rtma_data_0 - rtma_data_1
        diff2 = rtma_data_1 - rtma_data_2
        diff3 = rtma_data_2 - rtma_data_3
        diff4 = rtma_data_3 - rtma_data_4
        diff5 = rtma_data_4 - rtma_data_5
        diff6 = rtma_data_5 - rtma_data_6
        diff7 = rtma_data_6 - rtma_data_7

        plot_proj_8 = diff1.metpy.cartopy_crs
        plot_proj_9 = diff2.metpy.cartopy_crs
        plot_proj_10 = diff3.metpy.cartopy_crs
        plot_proj_11 = diff4.metpy.cartopy_crs
        plot_proj_12 = diff5.metpy.cartopy_crs
        plot_proj_13 = diff6.metpy.cartopy_crs
        plot_proj_14 = diff7.metpy.cartopy_crs

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        
        rtma_time_0 = rtma_time_0.replace(tzinfo=from_zone)
        rtma_time_0 = rtma_time_0.astimezone(to_zone)
        rtma_time_utc_0 = rtma_time_0.astimezone(from_zone)
        metar_time_revised_0 = metar_time_revised_0.replace(tzinfo=from_zone)
        metar_time_revised_0 = metar_time_revised_0.astimezone(to_zone)
        metar_time_revised_0_utc = metar_time_revised_0.astimezone(from_zone)

        rtma_time_1 = rtma_time_1.replace(tzinfo=from_zone)
        rtma_time_1 = rtma_time_1.astimezone(to_zone)
        rtma_time_utc_1 = rtma_time_1.astimezone(from_zone)
        metar_time_revised_1 = metar_time_revised_1.replace(tzinfo=from_zone)
        metar_time_revised_1 = metar_time_revised_1.astimezone(to_zone)
        metar_time_revised_1_utc = metar_time_revised_1.astimezone(from_zone)

        rtma_time_2 = rtma_time_2.replace(tzinfo=from_zone)
        rtma_time_2 = rtma_time_2.astimezone(to_zone)
        rtma_time_utc_2 = rtma_time_2.astimezone(from_zone)
        metar_time_revised_2 = metar_time_revised_2.replace(tzinfo=from_zone)
        metar_time_revised_2 = metar_time_revised_2.astimezone(to_zone)
        metar_time_revised_2_utc = metar_time_revised_2.astimezone(from_zone)

        rtma_time_3 = rtma_time_3.replace(tzinfo=from_zone)
        rtma_time_3 = rtma_time_3.astimezone(to_zone)
        rtma_time_utc_3 = rtma_time_3.astimezone(from_zone)
        metar_time_revised_3 = metar_time_revised_3.replace(tzinfo=from_zone)
        metar_time_revised_3 = metar_time_revised_3.astimezone(to_zone)
        metar_time_revised_3_utc = metar_time_revised_3.astimezone(from_zone)

        rtma_time_4 = rtma_time_4.replace(tzinfo=from_zone)
        rtma_time_4 = rtma_time_4.astimezone(to_zone)
        rtma_time_utc_4 = rtma_time_4.astimezone(from_zone)
        metar_time_revised_4 = metar_time_revised_4.replace(tzinfo=from_zone)
        metar_time_revised_4 = metar_time_revised_4.astimezone(to_zone)
        metar_time_revised_4_utc = metar_time_revised_4.astimezone(from_zone)

        rtma_time_5 = rtma_time_5.replace(tzinfo=from_zone)
        rtma_time_5 = rtma_time_5.astimezone(to_zone)
        rtma_time_utc_5 = rtma_time_5.astimezone(from_zone)
        metar_time_revised_5 = metar_time_revised_5.replace(tzinfo=from_zone)
        metar_time_revised_5 = metar_time_revised_5.astimezone(to_zone)
        metar_time_revised_5_utc = metar_time_revised_5.astimezone(from_zone)

        rtma_time_6 = rtma_time_6.replace(tzinfo=from_zone)
        rtma_time_6 = rtma_time_6.astimezone(to_zone)
        rtma_time_utc_6 = rtma_time_6.astimezone(from_zone)
        metar_time_revised_6 = metar_time_revised_6.replace(tzinfo=from_zone)
        metar_time_revised_6 = metar_time_revised_6.astimezone(to_zone)
        metar_time_revised_6_utc = metar_time_revised_6.astimezone(from_zone)

        rtma_time_7 = rtma_time_7.replace(tzinfo=from_zone)
        rtma_time_7 = rtma_time_7.astimezone(to_zone)
        rtma_time_utc_7 = rtma_time_7.astimezone(from_zone)
        metar_time_revised_7 = metar_time_revised_7.replace(tzinfo=from_zone)
        metar_time_revised_7 = metar_time_revised_7.astimezone(to_zone)
        metar_time_revised_7_utc = metar_time_revised_7.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()
        
        cmap_trend = colormaps.relative_humidity_change_colormap()

        figs = []

        ################
        # FIRST FIGURE #
        ################

        fig1 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig1.set_facecolor('aliceblue')

        fig1.suptitle("METAR RH (Numbers) + RTMA Hourly RH Trend (Shaded)\nMETAR Valid: " + metar_time_revised_0.strftime('%H:00 Local') + " (" + metar_time_revised_0_utc.strftime('%H:00 UTC')+")\nRTMA RH Trend Valid: "+rtma_time_0.strftime('%H:00 Local') + " (" + rtma_time_utc_0.strftime('%H:00 UTC')+")" + " - " + rtma_time_1.strftime('%H:00 Local') + " (" + rtma_time_utc_1.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')

        ax1 = fig1.add_subplot(1, 1, 1, projection=plot_proj_8)
        ax1.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax1.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax1.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs1 = ax1.contourf(diff1.metpy.x, diff1.metpy.y, diff1, 
                         transform=diff1.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap=cmap_trend, alpha=1, extend='both')

        cbar1 = fig1.colorbar(cs1, shrink=color_table_shrink, pad=colorbar_pad)
        cbar1.set_label(label="Hourly Relative Humidity Trend (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn1 = mpplots.StationPlot(ax1, sfc_data_0['longitude'][sfc_data_mask_0].m, sfc_data_0['latitude'][sfc_data_mask_0].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn1.plot_parameter('C', sfc_data_rh_0.to('percent')[sfc_data_mask_0], color='black',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        

        ax1.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax1.transAxes)


        #################
        # SECOND FIGURE #
        #################

        fig2 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig2.set_facecolor('aliceblue')

        fig2.suptitle("METAR RH (Numbers) + RTMA Hourly RH Trend (Shaded)\nMETAR Valid: " + metar_time_revised_1.strftime('%H:00 Local') + " (" + metar_time_revised_1_utc.strftime('%H:00 UTC')+")\nRTMA RH Trend Valid: "+rtma_time_1.strftime('%H:00 Local') + " (" + rtma_time_utc_1.strftime('%H:00 UTC')+")" + " - " + rtma_time_2.strftime('%H:00 Local') + " (" + rtma_time_utc_2.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')

        ax2 = fig2.add_subplot(1, 1, 1, projection=plot_proj_9)
        ax2.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax2.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax2.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs2 = ax2.contourf(diff2.metpy.x, diff2.metpy.y, diff2, 
                         transform=diff2.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap=cmap_trend, alpha=1, extend='both')

        cbar2 = fig2.colorbar(cs2, shrink=color_table_shrink, pad=colorbar_pad)
        cbar2.set_label(label="Hourly Relative Humidity Trend (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn2 = mpplots.StationPlot(ax2, sfc_data_1['longitude'][sfc_data_mask_1].m, sfc_data_1['latitude'][sfc_data_mask_1].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
    
        stn2.plot_parameter('C', sfc_data_rh_1.to('percent')[sfc_data_mask_1], color='black',
                            path_effects=[withStroke(linewidth=1, foreground='black')])


        ax2.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax2.transAxes)


        ################
        # THIRD FIGURE #
        ################

        fig3 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig3.set_facecolor('aliceblue')

        fig3.suptitle("METAR RH (Numbers) + RTMA Hourly RH Trend (Shaded)\nMETAR Valid: " + metar_time_revised_2.strftime('%H:00 Local') + " (" + metar_time_revised_2_utc.strftime('%H:00 UTC')+")\nRTMA RH Trend Valid: "+rtma_time_2.strftime('%H:00 Local') + " (" + rtma_time_utc_2.strftime('%H:00 UTC')+")" + " - " + rtma_time_3.strftime('%H:00 Local') + " (" + rtma_time_utc_3.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')

        ax3 = fig3.add_subplot(1, 1, 1, projection=plot_proj_10)
        ax3.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax3.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax3.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax3.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax3.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax3.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs3 = ax3.contourf(diff3.metpy.x, diff3.metpy.y, diff3, 
                         transform=diff3.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap=cmap_trend, alpha=1, extend='both')

        cbar3 = fig3.colorbar(cs3, shrink=color_table_shrink, pad=colorbar_pad)
        cbar3.set_label(label="Hourly Relative Humidity Trend (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn3 = mpplots.StationPlot(ax3, sfc_data_2['longitude'][sfc_data_mask_2].m, sfc_data_2['latitude'][sfc_data_mask_2].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn3.plot_parameter('C', sfc_data_rh_2.to('percent')[sfc_data_mask_2], color='black',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        

        ax3.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax3.transAxes)


        #################
        # FOURTH FIGURE #
        #################

        fig4 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig4.set_facecolor('aliceblue')

        fig4.suptitle("METAR RH (Numbers) + RTMA Hourly RH Trend (Shaded)\nMETAR Valid: " + metar_time_revised_3.strftime('%H:00 Local') + " (" + metar_time_revised_3_utc.strftime('%H:00 UTC')+")\nRTMA RH Trend Valid: "+rtma_time_3.strftime('%H:00 Local') + " (" + rtma_time_utc_3.strftime('%H:00 UTC')+")" + " - " + rtma_time_4.strftime('%H:00 Local') + " (" + rtma_time_utc_4.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')

        ax4 = fig4.add_subplot(1, 1, 1, projection=plot_proj_11)
        ax4.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax4.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax4.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax4.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax4.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax4.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax4.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax4.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs4 = ax4.contourf(diff4.metpy.x, diff4.metpy.y, diff4, 
                         transform=diff4.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap=cmap_trend, alpha=1, extend='both')

        cbar4 = fig4.colorbar(cs4, shrink=color_table_shrink, pad=colorbar_pad)
        cbar4.set_label(label="Hourly Relative Humidity Trend (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn4 = mpplots.StationPlot(ax4, sfc_data_3['longitude'][sfc_data_mask_3].m, sfc_data_3['latitude'][sfc_data_mask_3].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        stn4.plot_parameter('E', sfc_data_rh_3.to('percent')[sfc_data_mask_3], color='black',
                            path_effects=[withStroke(linewidth=1, foreground='black')])

        ax4.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax4.transAxes)


        ################
        # FIFTH FIGURE #
        ################

        fig5 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig5.set_facecolor('aliceblue')

        fig5.suptitle("METAR RH (Numbers) + RTMA Hourly RH Trend (Shaded)\nMETAR Valid: " + metar_time_revised_4.strftime('%H:00 Local') + " (" + metar_time_revised_4_utc.strftime('%H:00 UTC')+")\nRTMA RH Trend Valid: "+rtma_time_4.strftime('%H:00 Local') + " (" + rtma_time_utc_4.strftime('%H:00 UTC')+")" + " - " + rtma_time_5.strftime('%H:00 Local') + " (" + rtma_time_utc_5.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')

        ax5 = fig5.add_subplot(1, 1, 1, projection=plot_proj_12)
        ax5.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax5.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax5.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax5.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax5.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax5.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax5.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax5.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs5 = ax5.contourf(diff5.metpy.x, diff5.metpy.y, diff5, 
                         transform=diff5.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap=cmap_trend, alpha=1, extend='both')

        cbar5 = fig5.colorbar(cs5, shrink=color_table_shrink, pad=colorbar_pad)
        cbar5.set_label(label="Hourly Relative Humidity Trend (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn5 = mpplots.StationPlot(ax5, sfc_data_4['longitude'][sfc_data_mask_4].m, sfc_data_4['latitude'][sfc_data_mask_4].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn5.plot_parameter('E', sfc_data_rh_4.to('percent')[sfc_data_mask_4], color='black',
                            path_effects=[withStroke(linewidth=1, foreground='black')])


        ax5.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax5.transAxes)

        ################
        # SIXTH FIGURE #
        ################

        fig6 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig6.set_facecolor('aliceblue')

        fig6.suptitle("METAR RH (Numbers) + RTMA Hourly RH Trend (Shaded)\nMETAR Valid: " + metar_time_revised_5.strftime('%H:00 Local') + " (" + metar_time_revised_5_utc.strftime('%H:00 UTC')+")\nRTMA RH Trend Valid: "+rtma_time_5.strftime('%H:00 Local') + " (" + rtma_time_utc_5.strftime('%H:00 UTC')+")" + " - " + rtma_time_6.strftime('%H:00 Local') + " (" + rtma_time_utc_6.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')

        ax6 = fig6.add_subplot(1, 1, 1, projection=plot_proj_13)
        ax6.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax6.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax6.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax6.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax6.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax6.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax6.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax6.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs6 = ax6.contourf(diff6.metpy.x, diff6.metpy.y, diff6, 
                         transform=diff6.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap=cmap_trend, alpha=1, extend='both')

        cbar6 = fig6.colorbar(cs6, shrink=color_table_shrink, pad=colorbar_pad)
        cbar6.set_label(label="Hourly Relative Humidity Trend (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn6 = mpplots.StationPlot(ax6, sfc_data_5['longitude'][sfc_data_mask_5].m, sfc_data_5['latitude'][sfc_data_mask_5].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)

        
        stn6.plot_parameter('C', sfc_data_rh_5.to('percent')[sfc_data_mask_5], color='black',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        ax6.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax6.transAxes)

        ##################
        # SEVENTH FIGURE #
        ##################

        fig7 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig7.set_facecolor('aliceblue')

        fig7.suptitle("METAR RH (Numbers) + RTMA Hourly RH Trend (Shaded)\nMETAR Valid: " + metar_time_revised_6.strftime('%H:00 Local') + " (" + metar_time_revised_6_utc.strftime('%H:00 UTC')+")\nRTMA RH Trend Valid: "+rtma_time_6.strftime('%H:00 Local') + " (" + rtma_time_utc_6.strftime('%H:00 UTC')+")" + " - " + rtma_time_7.strftime('%H:00 Local') + " (" + rtma_time_utc_7.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')

        ax7 = fig7.add_subplot(1, 1, 1, projection=plot_proj_14)
        ax7.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax7.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax7.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax7.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax7.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax7.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax7.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax7.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs7 = ax7.contourf(diff7.metpy.x, diff7.metpy.y, diff7, 
                         transform=diff7.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap=cmap_trend, alpha=1, extend='both')

        cbar7 = fig7.colorbar(cs7, shrink=color_table_shrink, pad=colorbar_pad)
        cbar7.set_label(label="Hourly Relative Humidity Trend (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn7 = mpplots.StationPlot(ax7, sfc_data_6['longitude'][sfc_data_mask_6].m, sfc_data_6['latitude'][sfc_data_mask_6].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        stn7.plot_parameter('C', sfc_data_rh_6.to('percent')[sfc_data_mask_6], color='black',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        ax7.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax7.transAxes)

        figs.append(fig7)
        figs.append(fig6)
        figs.append(fig5)
        figs.append(fig4)
        figs.append(fig3)
        figs.append(fig2)
        figs.append(fig1)

        return figs
    

    def plot_red_flag_relative_humidity_with_METARs(red_flag_warning_relative_humidity_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, mask, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the relative humidity data filtered RH <= red_flag_warning_relative_humidity_threshold (%) overlayed with the latest METAR reports. 

            

            Inputs:

                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity data filtered RH <= red_flag_warning_relative_humidity_threshold (%) overlayed with the latest METAR reports. 
        
        '''

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold
        red_flag_warning_relative_humidity_threshold_numpy = red_flag_warning_relative_humidity_threshold + 1
        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(utc_time, mask)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        metar_time_revised = metar_time_revised.replace(tzinfo=from_zone)
        metar_time_revised = metar_time_revised.astimezone(to_zone)
        metar_time_revised_utc = metar_time_revised.astimezone(from_zone)

        cmap = colormaps.low_relative_humidity_colormap()
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(0, red_flag_warning_relative_humidity_threshold_numpy, 1), cmap=cmap, alpha=1)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn = mpplots.StationPlot(ax, sfc_data['longitude'][sfc_data_mask].m, sfc_data['latitude'][sfc_data_mask].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn.plot_parameter('NW', sfc_data['air_temperature'].to('degF')[sfc_data_mask], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_parameter('SW', sfc_data['dew_point_temperature'].to('degF')[sfc_data_mask], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_symbol('C', sfc_data['cloud_coverage'][sfc_data_mask], mpplots.sky_cover)
        
        stn.plot_parameter('C', sfc_data_rh.to('percent')[sfc_data_mask], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_barb(sfc_data['u'][sfc_data_mask], sfc_data['v'][sfc_data_mask])

        plt.title("Real Time Mesoscale Analysis\nExceptionally Low Relative Humidity (RH <= "+ str(red_flag_warning_relative_humidity_threshold) +"%)\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_low_and_high_relative_humidity(low_relative_humidity_threshold, high_relative_humidity_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the relative humidity data filtered RH <= low_relative_humidity_threshold (%) and RH >= high_relative_humidity_threshold (%)

            

            Inputs:

                1) low_relative_humidity_threshold (Integer) - The user defines the threshold for what is considered low relative humidity for the respective geographic area.  

                2) high_relative_humidity_threshold (Integer) - The user defines the threshold for what is considered high relative humidity for the respective geographic area.  

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                14) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                15) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                16) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                17) title_font_size (Integer) - The fontsize of the title of the figure. 

                18) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                19) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                20) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                21) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity data filtered RH <= red_flag_warning_relative_humidity_threshold (%) overlayed with the latest METAR reports. 
        
        '''
        colorbar_label_font_size = colorbar_label_font_size

        colorbar_pad = colorbar_pad

        low_relative_humidity_threshold = low_relative_humidity_threshold
        low_relative_humidity_threshold_scale = low_relative_humidity_threshold + 1

        high_relative_humidity_threshold = high_relative_humidity_threshold
        high_relative_humidity_threshold_scale = high_relative_humidity_threshold

        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_relative_humidity_data(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        cmap_high = colormaps.excellent_recovery_colormap()
        cmap_low = colormaps.low_relative_humidity_colormap()

        plot_proj = rtma_data.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs_low = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(0, low_relative_humidity_threshold_scale, 1), cmap=cmap_low, alpha=1)

        cs_high = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(high_relative_humidity_threshold_scale, 101, 1), cmap=cmap_high, alpha=1)

        cbar_low = fig.colorbar(cs_low, location='left', shrink=color_table_shrink, pad=colorbar_pad)
        cbar_low.set_label(label="Low Relative Humidity (RH <=" + str(low_relative_humidity_threshold) +"%)", size=colorbar_label_font_size, fontweight='bold')

        cbar_high = fig.colorbar(cs_high, location='right', shrink=color_table_shrink, pad=colorbar_pad)
        cbar_high.set_label(label="High Relative Humidity (RH >= " + str(high_relative_humidity_threshold) +"%)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("2.5km Real Time Mesoscale Analysis\nLow RH(<=" + str(low_relative_humidity_threshold) +"%) & High RH (RH >= " + str(high_relative_humidity_threshold) +"%)\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_24_hour_relative_humidity_change(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the temperature and dewpoint data arrays for the current time and the data arrays for 24 hours ago from the data arrays for the current time.
                                            2) Uses MetPy to calculate the relative humidity from the temperature and dewpoint data arrays for both times (current time and current time - 24 hours).
                                            3) Subtracts the relative humidity data array from 24 hours ago from the relative humidity data array of the current time (Current RH - RH from 24 hours ago).
                                            4) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of the difference between the current relative humidity data array from the relative humidity data array from 24 hours ago.
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the 24-Hour difference with respect to relative humidity (%)
        
        '''


        local_time, utc_time = standard.plot_creation_time()
        
        cmap = colormaps.relative_humidity_change_colormap()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_rtma_relative_humidity_24_hour_difference_data(utc_time)

        rtma_time_24 = rtma_time - timedelta(hours=24)
        
        
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
        rtma_time_24 = rtma_time_24.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        rtma_time_24_utc = rtma_time_24.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        plot_proj = rtma_data.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-60, 65, 5), cmap=cmap, alpha=1, extend='both')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Relative Humidity Change (%)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA 24-Hour Relative Humidity Change (%)\nAnalysis Start: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_24_utc.strftime('%H:00 UTC')+ ")\nAnalysis End:" + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig



    def plot_24_hour_temperature_change(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the temperature data arrays for the current time and the data arrays for 24 hours ago from the data arrays for the current time.
                                            2) Converts the temperature values from Kelvin to Fahrenheit. 
                                            3) Subtracts the temperature data array from 24 hours ago from the temperature data array of the current time (Current Temperature - Temperature from 24 hours ago).
                                            4) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of the difference between the current temperature data array from the temperature data array from 24 hours ago.
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the 24-Hour difference with respect to temperature (degrees Fahrenheit)
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_rtma_data_24_hour_difference(utc_time, 'Temperature_Analysis_height_above_ground')

        rtma_time_24 = rtma_time - timedelta(hours=24)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
        rtma_time_24 = rtma_time_24.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        rtma_time_24_utc = rtma_time_24.astimezone(from_zone)

        rtma_data = calc.unit_conversion.Temperature_Or_Dewpoint_Change_to_Fahrenheit(rtma_data)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        plot_proj = rtma_data.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='lime', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap='seismic', alpha=1, extend='both')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Temperature Change (\N{DEGREE SIGN}F)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA 24-Hour Temperature Change (\N{DEGREE SIGN}F)\nAnalysis Start: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_24_utc.strftime('%H:00 UTC')+ ")\nAnalysis End:" + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_24_hour_wind_speed_change(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the wind speed data arrays for the current time and the data arrays for 24 hours ago from the data arrays for the current time.
                                            2) Converts wind speed values from m/s to MPH. 
                                            3) Subtracts the wind speed data array from 24 hours ago from the wind speed data array of the current time (Current Wind Speed - Wind Speed from 24 hours ago).
                                            4) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of the difference between the current wind speed data array from the wind speed data array from 24 hours ago.
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the 24-Hour difference with respect to wind speed (MPH). 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_rtma_data_24_hour_difference(utc_time, 'Wind_speed_Analysis_height_above_ground')

        rtma_time_24 = rtma_time - timedelta(hours=24)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
        rtma_time_24 = rtma_time_24.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        rtma_time_24_utc = rtma_time_24.astimezone(from_zone)

        rtma_data = rtma_data * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        plot_proj = rtma_data.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-30, 31, 1), cmap='PuOr_r', alpha=1, extend='both')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Wind Speed Change (MPH)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA 24-Hour Wind Speed Change (MPH)\nAnalysis Start: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_24_utc.strftime('%H:00 UTC')+ ")\nAnalysis End:" + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_current_frost_freeze_areas(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature data array.
                                            2) Converts temperature from Kelvin to Fahrenheit
                                            3) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of temperature filtered to only areas where T <= 32F. 
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis of temperature filtered to only areas where T <= 32F. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, 'Temperature_Analysis_height_above_ground')

        rtma_data = calc.unit_conversion.RTMA_Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(rtma_data)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        cmap = colormaps.cool_temperatures_colormap()

        plot_proj = rtma_data.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=state_border_linewidth, edgecolor='red', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-10, 33, 1), cmap=cmap, alpha=1, extend='min')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Temperature (\N{DEGREE SIGN}F)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA Current Frost & Freeze Areas (T <= 32\N{DEGREE SIGN}F)\n   Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC') + ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_dry_and_windy_areas_based_on_sustained_winds(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_speed_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_font_size, signature_font_size, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind speed data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind speed data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Speed >= red_flag_warning_wind_speed_threshold (MPH). 
                                            5) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis for areas where the aforementioned "Dry and Windy" criteria are met. 
            

            Inputs:

                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_speed_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis showing current areas of dry and windy conditions. 
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap = colormaps.red_flag_warning_criteria_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_speed_threshold = red_flag_warning_wind_speed_threshold

        rtma_rh, rtma_wind, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_speed(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_wind = rtma_wind * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_wind >= red_flag_warning_wind_speed_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj = mask.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        # Plot the mask
        try:
            ax.pcolormesh(lon,lat,mask,transform=ccrs.PlateCarree(),cmap=cmap, zorder=2)

        except Exception as e:
            pass
            

        plt.title("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Wind Speed >= " + str(red_flag_warning_wind_speed_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_dry_and_windy_areas_based_on_wind_gusts(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_gust_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_font_size, signature_font_size, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind gust data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind gust data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Gust >= red_flag_warning_wind_gust_threshold (MPH). 
                                            5) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis for areas where the aforementioned "Dry and Windy" criteria are met. 
            

            Inputs:

                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_gust_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed using wind gusts. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis showing current areas of dry and windy conditions. 
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap = colormaps.red_flag_warning_criteria_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_gust_threshold = red_flag_warning_wind_gust_threshold

        rtma_rh, rtma_gust, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_gust(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_gust = rtma_gust * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_gust >= red_flag_warning_wind_gust_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj = mask.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        ax.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)

        # Plot the mask
        try:
            ax.pcolormesh(lon,lat,mask,transform=ccrs.PlateCarree(),cmap=cmap, zorder=2)

        except Exception as e:
            pass
            

        plt.title("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Wind Gust >= " + str(red_flag_warning_wind_gust_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_dry_and_windy_areas_based_on_sustained_winds_3_panel(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_speed_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, plot_title_font_size, subplot_title_font_size, colorbar_shrink, colorbar_pad, colorbar_label_font_size, signature_x_position, signature_y_position, signature_font_size,  first_subplot_aspect_ratio, subsequent_subplot_aspect_ratio, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind speed data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind speed data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Speed >= red_flag_warning_wind_speed_threshold (MPH). 
                                            5) Plots a figure that consists of 3 subplots.
                                            List of subplots:
                                                        1) Plot where the dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_speed_threshold (MPH)
                                             
            

            Inputs:


                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_speed_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed.

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) color_table_shrink (Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                19) subplot_title_font_size (Integer) - Fontsize of all subplot titles. 
                
                20) first_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the first subplot. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size. 
                
                21) subsequent_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the second, third and fourth subplots. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size.

                22) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                23) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure showing the four aforementioned subplots:                                                             
                                                        1) Plot where the hot, dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_speed_threshold (MPH)
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap_rfw = colormaps.red_flag_warning_criteria_colormap()
        cmap_rh = colormaps.low_relative_humidity_colormap()
        cmap_wind = colormaps.red_flag_warning_wind_parameter_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_speed_threshold = red_flag_warning_wind_speed_threshold

        rtma_rh, rtma_wind, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_speed(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_wind = rtma_wind * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_wind >= red_flag_warning_wind_speed_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj_1 = mask.metpy.cartopy_crs
        plot_proj_2 = rtma_rh.metpy.cartopy_crs
        plot_proj_3 = rtma_wind.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')
        gs = gridspec.GridSpec(1, 9)
        ax0 = fig.add_subplot(gs[0:1, 0:3], projection=plot_proj_1)
        ax0.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax0.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax0.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax0.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax0.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax0.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        if show_rivers == True:
            ax0.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax0.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)
        ax0.set_aspect(first_subplot_aspect_ratio)
        ax0.set_title("Exceptionally Dry & Windy Areas", fontsize=subplot_title_font_size, fontweight='bold')

        # Plot the mask
        try:
            ax0.pcolormesh(lon,lat,mask, transform=ccrs.PlateCarree(),cmap=cmap_rfw, zorder=2)

        except Exception as e:
            pass


        ax1 = fig.add_subplot(gs[0:1, 3:6], projection=plot_proj_2)
        ax1.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        if show_rivers == True:
            ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax1.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)
        ax1.set_aspect(subsequent_subplot_aspect_ratio)
        ax1.set_title("Low Relative Humidity Areas", fontsize=subplot_title_font_size, fontweight='bold')

        cs_rh = ax1.contourf(rtma_rh.metpy.x, rtma_rh.metpy.y, rtma_rh, 
                         transform=rtma_rh.metpy.cartopy_crs, levels=np.arange(0, 16, 1), cmap=cmap_rh, alpha=1)

        cbar_rh = fig.colorbar(cs_rh, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_rh.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')


        ax2 = fig.add_subplot(gs[0:1, 6:9], projection=plot_proj_3)
        ax2.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        if show_rivers == True:
            ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax2.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)
        ax2.set_aspect(subsequent_subplot_aspect_ratio)
        ax2.set_title("Sustained Wind Speed", fontsize=subplot_title_font_size, fontweight='bold')

        cs_wind = ax2.contourf(rtma_wind.metpy.x, rtma_wind.metpy.y, rtma_wind, 
                         transform=rtma_wind.metpy.cartopy_crs, levels=np.arange(25, 75, 5), cmap=cmap_wind, alpha=1)

        cbar_wind = fig.colorbar(cs_wind, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_wind.set_label(label="Sustained Wind Speed (MPH)", size=colorbar_label_font_size, fontweight='bold')   
        

        fig.suptitle("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Sustained Wind Speed >= " + str(red_flag_warning_wind_speed_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=plot_title_font_size, fontweight='bold')
        
        ax0.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy\n(C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax0.transAxes)

        return fig        


    def plot_dry_and_windy_areas_based_on_wind_gusts_3_panel(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_gust_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, plot_title_font_size, subplot_title_font_size, colorbar_shrink, colorbar_pad, colorbar_label_font_size, signature_x_position, signature_y_position, signature_font_size,  first_subplot_aspect_ratio, subsequent_subplot_aspect_ratio, show_rivers, state_border_linewidth, county_border_linewidth):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind gust data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind gust data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Gust >= red_flag_warning_wind_gust_threshold (MPH). 
                                            5) Plots a figure that consists of 3 subplots.
                                            List of subplots:
                                                        1) Plot where the dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_gust_threshold (MPH)
                                             
            

            Inputs:


                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_gust_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed using wind gusts. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) color_table_shrink (Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                19) subplot_title_font_size (Integer) - Fontsize of all subplot titles. 
                
                20) first_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the first subplot. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size. 
                
                21) subsequent_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the second, third and fourth subplots. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size.

                22) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                23) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure showing the four aforementioned subplots:                                                             
                                                        1) Plot where the hot, dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_speed_threshold (MPH)
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap_rfw = colormaps.red_flag_warning_criteria_colormap()
        cmap_rh = colormaps.low_relative_humidity_colormap()
        cmap_wind = colormaps.red_flag_warning_wind_parameter_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_gust_threshold = red_flag_warning_wind_gust_threshold

        rtma_rh, rtma_wind, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_gust(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_wind = rtma_wind * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_wind >= red_flag_warning_wind_gust_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj_1 = mask.metpy.cartopy_crs
        plot_proj_2 = rtma_rh.metpy.cartopy_crs
        plot_proj_3 = rtma_wind.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')
        gs = gridspec.GridSpec(1, 9)
        ax0 = fig.add_subplot(gs[0:1, 0:3], projection=plot_proj_1)
        ax0.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax0.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax0.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax0.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax0.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax0.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        if show_rivers == True:
            ax0.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax0.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)
        ax0.set_aspect(first_subplot_aspect_ratio)
        ax0.set_title("Exceptionally Dry & Windy Areas", fontsize=subplot_title_font_size, fontweight='bold')

        # Plot the mask
        try:
            ax0.pcolormesh(lon,lat,mask, transform=ccrs.PlateCarree(),cmap=cmap_rfw, zorder=2)

        except Exception as e:
            pass


        ax1 = fig.add_subplot(gs[0:1, 3:6], projection=plot_proj_2)
        ax1.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        if show_rivers == True:
            ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax1.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)
        ax1.set_aspect(subsequent_subplot_aspect_ratio)
        ax1.set_title("Low Relative Humidity Areas", fontsize=subplot_title_font_size, fontweight='bold')

        cs_rh = ax1.contourf(rtma_rh.metpy.x, rtma_rh.metpy.y, rtma_rh, 
                         transform=rtma_rh.metpy.cartopy_crs, levels=np.arange(0, 16, 1), cmap=cmap_rh, alpha=1)

        cbar_rh = fig.colorbar(cs_rh, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_rh.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')


        ax2 = fig.add_subplot(gs[0:1, 6:9], projection=plot_proj_3)
        ax2.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.STATES, linewidth=2, edgecolor='violet', zorder=5)
        if show_rivers == True:
            ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax2.add_feature(USCOUNTIES, linewidth=county_border_linewidth, zorder=4)
        ax2.set_aspect(subsequent_subplot_aspect_ratio)
        ax2.set_title("Wind Gust", fontsize=subplot_title_font_size, fontweight='bold')

        cs_wind = ax2.contourf(rtma_wind.metpy.x, rtma_wind.metpy.y, rtma_wind, 
                         transform=rtma_wind.metpy.cartopy_crs, levels=np.arange(25, 75, 5), cmap=cmap_wind, alpha=1)

        cbar_wind = fig.colorbar(cs_wind, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_wind.set_label(label="Wind Gust (MPH)", size=colorbar_label_font_size, fontweight='bold')   
        

        fig.suptitle("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Wind Gust >= " + str(red_flag_warning_wind_gust_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")", fontsize=plot_title_font_size, fontweight='bold')
        
        ax0.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy\n(C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax0.transAxes)

        return fig     


class Predictive_Services_Areas_Perspective:

    r'''
    This class hosts the graphics using Geographic Area Coordination Center (GACC) and Predictive Services Area (PSA) boundaries as the geographic reference. 
    '''
  
    def plot_generic_real_time_mesoanalysis_no_METARs(parameter, plot_title, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table, color_table_title, color_table_start, color_table_stop, color_table_step, color_table_shrink, GACC_Border_Color, GACC_Border_Line_Thickness, PSA_Border_Line_Thickness, PSA_Border_Color, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''

            This function does the following:
                                            1) Downloads the data that corresponds to the parameter the user requests. 
                                            2) Converts the units of the data (if needed).
                                            3) Plots the data that corresponds to the parameter the user requests. 

            

            Inputs:
                1) parameter (String) - The parameter the user chooses to plot. For the full parameter list, visit: https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/NDFD/NWS/CONUS/CONDUIT/Best.html

                2) plot_title (String) - The title of the entire figure. 

                3) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                4) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                5) color_table (String) - The color table used for the scale of the data being plotted. See either the FireWxPy and/or matplotlib colortable documentation for colortable options. 

                6) color_table_title (String) - The title along the colorbar on the edge of the figure. 

                7) color_table_start (Integer) - The bottom bound of the color scale reference used to plot the data. 

                8) color_table_stop (Integer) - The top bound of the color scale reference used to plot the data.

                9) color_table_step (Integer) - The increment of the color scale (i.e. every 1 degree vs. every 5 degrees). 

                10) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                11) GACC_Border_Color (String) - Color of the GACC border. 

                12) GACC_Border_Line_Thickness (Integer or Float) - Thickness of the GACC border lines. 

                13) PSA_Border_Line_Thickness (String) - Color of the PSA border. 

                14) PSA_Border_Color (Integer or Float) - Thickness of the PSA border lines.

                15) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                16) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                17) title_font_size (Integer) - The fontsize of the title of the figure. 

                18) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                19) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                20) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                21) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the parameter the user wishes to plot. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()
        param = parameter

        if param == 'Wind_speed_gust_Analysis_height_above_ground' or param == 'Wind_speed_Analysis_height_above_ground' or param == 'Wind_speed_error_height_above_ground' or param == 'Wind_speed_gust_error_height_above_ground' or param == 'u-component_of_wind_Analysis_height_above_ground' or param == 'v-component_of_wind_Analysis_height_above_ground':

            data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, param)
            data = data * 2.23694

        if param == 'Temperature_Analysis_height_above_ground' or param == 'Dewpoint_temperature_Analysis_height_above_ground' or param == 'Temperature_error_height_above_ground' or param == 'Dewpoint_temperature_error_height_above_ground':
            
            data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, param)
            data = calc.unit_conversion.RTMA_Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(data)
            

        else:
            data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, param)
            
        plot_proj = data.metpy.cartopy_crs

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", PSA_Border_Color)

        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", GACC_Border_Color)

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=GACC_Border_Line_Thickness, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=PSA_Border_Line_Thickness, zorder=4)

        cs = ax.contourf(data.metpy.x, data.metpy.y, data, 
                         transform=data.metpy.cartopy_crs, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, alpha=0.5)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label=color_table_title, size=colorbar_label_font_size, fontweight='bold')

        plt.title(plot_title + "\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_generic_real_time_mesoanalysis_with_METARs(parameter, plot_title, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table, color_table_title, color_table_start, color_table_stop, color_table_step, color_table_shrink, mask, GACC_Border_Color, GACC_Border_Line_Thickness, PSA_Border_Line_Thickness, PSA_Border_Color, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the data that corresponds to the parameter the user requests. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Converts the units of the data (if needed).
                                            4) Plots the data that corresponds to the parameter the user requests. 

            

            Inputs:
                1) parameter (String) - The parameter the user chooses to plot. For the full parameter list, visit: https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/NDFD/NWS/CONUS/CONDUIT/Best.html

                2) plot_title (String) - The title of the entire figure. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) color_table (String) - The color table used for the scale of the data being plotted. See either the FireWxPy and/or matplotlib colortable documentation for colortable options. 

                14) color_table_title (String) - The title along the colorbar on the edge of the figure. 

                15) color_table_start (Integer) - The bottom bound of the color scale reference used to plot the data. 

                16) color_table_stop (Integer) - The top bound of the color scale reference used to plot the data.

                17) color_table_step (Integer) - The increment of the color scale (i.e. every 1 degree vs. every 5 degrees). 

                18) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                19) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 
          
                19) GACC_Border_Color (String) - Color of the GACC border. 

                20) GACC_Border_Line_Thickness (Integer or Float) - Thickness of the GACC border lines. 

                21) PSA_Border_Line_Thickness (String) - Color of the PSA border. 

                22) PSA_Border_Color (Integer or Float) - Thickness of the PSA border lines.

                23) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                24) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                25) title_font_size (Integer) - The fontsize of the title of the figure. 

                26) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                27) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                28) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                29) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the parameter the user wishes to plot plus the METAR plots for the same time as the Real Time Mesoscale Analysis. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()
        param = parameter

        if param == 'Wind_speed_gust_Analysis_height_above_ground' or param == 'Wind_speed_Analysis_height_above_ground' or param == 'Wind_speed_error_height_above_ground' or param == 'Wind_speed_gust_error_height_above_ground' or param == 'u-component_of_wind_Analysis_height_above_ground' or param == 'v-component_of_wind_Analysis_height_above_ground':

           rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Synced_With_METAR(param, utc_time, mask)
           rtma_data = rtma_data * 2.23694

        if param == 'Temperature_Analysis_height_above_ground' or param == 'Dewpoint_temperature_Analysis_height_above_ground' or param == 'Temperature_error_height_above_ground' or param == 'Dewpoint_temperature_error_height_above_ground':
            
            rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Synced_With_METAR(param, utc_time, mask)
            rtma_data = calc.unit_conversion.RTMA_Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(rtma_data)
            

        else:
           rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Synced_With_METAR(param, utc_time, mask)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        metar_time_revised = metar_time_revised.astimezone(to_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", PSA_Border_Color)
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", GACC_Border_Color)

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=GACC_Border_Line_Thickness, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=PSA_Border_Line_Thickness, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(color_table_start, color_table_stop, color_table_step), cmap=color_table, alpha=0.5)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label=color_table_title, size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn = mpplots.StationPlot(ax, sfc_data['longitude'][sfc_data_mask].m, sfc_data['latitude'][sfc_data_mask].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn.plot_parameter('NW', sfc_data['air_temperature'].to('degF')[sfc_data_mask], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_parameter('SW', sfc_data['dew_point_temperature'].to('degF')[sfc_data_mask], color='blue',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_symbol('C', sfc_data['cloud_coverage'][sfc_data_mask], mpplots.sky_cover)
        
        stn.plot_parameter('E', sfc_data_rh.to('percent')[sfc_data_mask], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_barb(sfc_data['u'][sfc_data_mask], sfc_data['v'][sfc_data_mask])

        plt.title(plot_title + "\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised.strftime('%m/%d/%Y %H:00 Local')+ "\nMETAR Observations\nValid: " + metar_time_revised.strftime('%m/%d/%Y %H:00 Local'), fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig



    def plot_relative_humidity_with_METARs(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, mask, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the data that corresponds to the parameter the user requests. 

            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity overlayed with the latest METAR reports. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(utc_time, mask)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        metar_time_revised = metar_time_revised.replace(tzinfo=from_zone)
        metar_time_revised = metar_time_revised.astimezone(to_zone)
        metar_time_revised_utc = metar_time_revised.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'red')

        cmap = colormaps.relative_humidity_colormap()

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(0, 105, 5), cmap=cmap, alpha=1)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn = mpplots.StationPlot(ax, sfc_data['longitude'][sfc_data_mask].m, sfc_data['latitude'][sfc_data_mask].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn.plot_parameter('NW', sfc_data['air_temperature'].to('degF')[sfc_data_mask], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_parameter('SW', sfc_data['dew_point_temperature'].to('degF')[sfc_data_mask], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_symbol('C', sfc_data['cloud_coverage'][sfc_data_mask], mpplots.sky_cover)
        
        stn.plot_parameter('E', sfc_data_rh.to('percent')[sfc_data_mask], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_barb(sfc_data['u'][sfc_data_mask], sfc_data['v'][sfc_data_mask])

        plt.title("Real Time Mesoscale Analysis Relative Humidity\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_red_flag_relative_humidity_with_METARs(red_flag_warning_relative_humidity_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, mask, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Downloads the METAR Data that is synced with the latest availiable 2.5km x 2.5km Real Time Mesoscale Analysis Data. 
                                            3) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the relative humidity data filtered RH <= red_flag_warning_relative_humidity_threshold (%) overlayed with the latest METAR reports. 

            

            Inputs:

                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                19) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity data filtered RH <= red_flag_warning_relative_humidity_threshold (%) overlayed with the latest METAR reports. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold
        red_flag_warning_relative_humidity_threshold_numpy = red_flag_warning_relative_humidity_threshold + 1

        rtma_data, rtma_time, sfc_data, sfc_data_u_kt, sfc_data_v_kt, sfc_data_rh, sfc_data_mask, metar_time_revised, plot_proj = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.METARs.RTMA_Relative_Humidity_Synced_With_METAR(utc_time, mask)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        metar_time_revised = metar_time_revised.replace(tzinfo=from_zone)
        metar_time_revised = metar_time_revised.astimezone(to_zone)
        metar_time_revised_utc = metar_time_revised.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        cmap = colormaps.low_relative_humidity_colormap()

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'red')

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(0, red_flag_warning_relative_humidity_threshold_numpy, 1), cmap=cmap, alpha=1)

        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')

        # Plots METAR
        stn = mpplots.StationPlot(ax, sfc_data['longitude'][sfc_data_mask].m, sfc_data['latitude'][sfc_data_mask].m,
                                 transform=ccrs.PlateCarree(), fontsize=11, zorder=10, clip_on=True)
        
        
        stn.plot_parameter('NW', sfc_data['air_temperature'].to('degF')[sfc_data_mask], color='red',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_parameter('SW', sfc_data['dew_point_temperature'].to('degF')[sfc_data_mask], color='darkorange',
                          path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_symbol('C', sfc_data['cloud_coverage'][sfc_data_mask], mpplots.sky_cover)
        
        stn.plot_parameter('E', sfc_data_rh.to('percent')[sfc_data_mask], color='lime',
                            path_effects=[withStroke(linewidth=1, foreground='black')])
        
        stn.plot_barb(sfc_data['u'][sfc_data_mask], sfc_data['v'][sfc_data_mask])

        plt.title("Real Time Mesoscale Analysis\nExceptionally Low Relative Humidity (RH <= "+ str(red_flag_warning_relative_humidity_threshold) +"%)\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+")\nMETAR Observations\nValid: " + metar_time_revised.strftime('%m/%d/%Y %H:00 Local')+" ("+metar_time_revised_utc.strftime('%H:00 UTC')+")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_low_and_high_relative_humidity(low_relative_humidity_threshold, high_relative_humidity_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
        This function does the following:
                                            1) Downloads the latest availiable temperature and dewpoint data arrays. 
                                            2) Uses MetPy to calculate the relative humidity data array from the temperature and dewpoint data arrays. 
                                            4) Plots the relative humidity data filtered RH <= low_relative_humidity_threshold (%) and RH >= high_relative_humidity_threshold (%)

            

            Inputs:

                1) low_relative_humidity_threshold (Integer) - The user defines the threshold for what is considered low relative humidity for the respective geographic area.  

                2) high_relative_humidity_threshold (Integer) - The user defines the threshold for what is considered high relative humidity for the respective geographic area.  

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 
                
                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                14) mask (Integer) - Distance in meters to mask METAR stations apart from eachother so stations don't clutter the plot. The higher the value, the less stations are displayed. 

                15) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                16) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                17) title_font_size (Integer) - The fontsize of the title of the figure. 

                18) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                19) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                20) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot.

                21) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis relative humidity data filtered RH <= red_flag_warning_relative_humidity_threshold (%) overlayed with the latest METAR reports. 
        
        '''

        colorbar_label_font_size = colorbar_label_font_size

        colorbar_pad = colorbar_pad

        low_relative_humidity_threshold = low_relative_humidity_threshold
        low_relative_humidity_threshold_scale = low_relative_humidity_threshold + 1

        high_relative_humidity_threshold = high_relative_humidity_threshold
        high_relative_humidity_threshold_scale = high_relative_humidity_threshold
        
        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_relative_humidity_data(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        cmap_low = colormaps.low_relative_humidity_colormap()
        cmap_high = colormaps.excellent_recovery_colormap()

        plot_proj = rtma_data.metpy.cartopy_crs

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'red')

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        cs_low = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(0, low_relative_humidity_threshold_scale, 1), cmap=cmap_low, alpha=1)

        cs_high = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(high_relative_humidity_threshold_scale, 101, 1), cmap=cmap_high, alpha=1)

        cbar_low = fig.colorbar(cs_low, location='left', shrink=color_table_shrink, pad=colorbar_pad)
        cbar_low.set_label(label="Low Relative Humidity (RH <="+ str(low_relative_humidity_threshold)+"%)", size=colorbar_label_font_size, fontweight='bold')

        cbar_high = fig.colorbar(cs_high, location='right', shrink=color_table_shrink, pad=colorbar_pad)
        cbar_high.set_label(label="High Relative Humidity (RH >="+ str(high_relative_humidity_threshold)+"%)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("2.5km Real Time Mesoscale Analysis\nLow RH(<="+ str(low_relative_humidity_threshold) +"%) & High RH (RH >="+ str(high_relative_humidity_threshold) +"%)\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_24_hour_relative_humidity_change(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the temperature and dewpoint data arrays for the current time and the data arrays for 24 hours ago from the data arrays for the current time.
                                            2) Uses MetPy to calculate the relative humidity from the temperature and dewpoint data arrays for both times (current time and current time - 24 hours).
                                            3) Subtracts the relative humidity data array from 24 hours ago from the relative humidity data array of the current time (Current RH - RH from 24 hours ago).
                                            4) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of the difference between the current relative humidity data array from the relative humidity data array from 24 hours ago.
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the 24-Hour difference with respect to relative humidity (%)
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_rtma_relative_humidity_24_hour_difference_data(utc_time)

        rtma_time_24 = rtma_time - timedelta(hours=24)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
        rtma_time_24 = rtma_time_24.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        rtma_time_24_utc = rtma_time_24.astimezone(from_zone)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        plot_proj = rtma_data.metpy.cartopy_crs

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'red')
        cmap = colormaps.relative_humidity_change_colormap()

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-60, 65, 5), cmap=cmap, alpha=1, extend='both')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Relative Humidity Change (%)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA 24-Hour Relative Humidity Change (%)\nAnalysis Start: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_24_utc.strftime('%H:00 UTC')+ ")\nAnalysis End:" + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_24_hour_temperature_change(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the temperature data arrays for the current time and the data arrays for 24 hours ago from the data arrays for the current time.
                                            2) Converts the temperature values from Kelvin to Fahrenheit. 
                                            3) Subtracts the temperature data array from 24 hours ago from the temperature data array of the current time (Current Temperature - Temperature from 24 hours ago).
                                            4) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of the difference between the current temperature data array from the temperature data array from 24 hours ago.
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the 24-Hour difference with respect to temperature (degrees Fahrenheit)
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_rtma_data_24_hour_difference(utc_time, 'Temperature_Analysis_height_above_ground')

        rtma_time_24 = rtma_time - timedelta(hours=24)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
        rtma_time_24 = rtma_time_24.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        rtma_time_24_utc = rtma_time_24.astimezone(from_zone)

        rtma_data = calc.unit_conversion.Temperature_Or_Dewpoint_Change_to_Fahrenheit(rtma_data)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        plot_proj = rtma_data.metpy.cartopy_crs

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'lime')

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-25, 26, 1), cmap='seismic', alpha=1, extend='both')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Temperature Change (\N{DEGREE SIGN}F)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA 24-Hour Temperature Change (\N{DEGREE SIGN}F)\nAnalysis Start: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_24_utc.strftime('%H:00 UTC')+ ")\nAnalysis End:" + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_24_hour_wind_speed_change(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the wind speed data arrays for the current time and the data arrays for 24 hours ago from the data arrays for the current time.
                                            2) Converts wind speed values from m/s to MPH. 
                                            3) Subtracts the wind speed data array from 24 hours ago from the wind speed data array of the current time (Current Wind Speed - Wind Speed from 24 hours ago).
                                            4) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of the difference between the current wind speed data array from the wind speed data array from 24 hours ago.
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis for the 24-Hour difference with respect to wind speed (MPH). 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_rtma_data_24_hour_difference(utc_time, 'Wind_speed_Analysis_height_above_ground')

        rtma_time_24 = rtma_time - timedelta(hours=24)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_24 = rtma_time_24.replace(tzinfo=from_zone)
        rtma_time_24 = rtma_time_24.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)
        rtma_time_24_utc = rtma_time_24.astimezone(from_zone)
        
        rtma_data = rtma_data * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'red')

        plot_proj = rtma_data.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-30, 31, 1), cmap='PuOr_r', alpha=1, extend='both')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Wind Speed Change (MPH)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA 24-Hour Wind Speed Change (MPH)\nAnalysis Start: " + rtma_time_24.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_24_utc.strftime('%H:00 UTC')+ ")\nAnalysis End:" + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC') + ")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig
        

    def plot_current_frost_freeze_areas(western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, color_table_shrink, signature_x_position, signature_y_position, title_font_size, signature_font_size, colorbar_label_font_size, colorbar_pad, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature data array.
                                            2) Converts temperature from Kelvin to Fahrenheit
                                            3) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis of temperature filtered to only areas where T <= 32F. 
            

            Inputs:

                1) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                2) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                3) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                4) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                5) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                6) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                7) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                8) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                9) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                10) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                11) color_table_shrink (Integer or Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                14) title_font_size (Integer) - The fontsize of the title of the figure. 

                15) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                16) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                17) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                18) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis of temperature filtered to only areas where T <= 32F. 
        
        '''


        local_time, utc_time = standard.plot_creation_time()

        rtma_data, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_current_rtma_data(utc_time, 'Temperature_Analysis_height_above_ground')

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_data = calc.unit_conversion.RTMA_Temperature_Data_or_Dewpoint_Data_Kelvin_to_Fahrenheit(rtma_data)
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()

        cmap = colormaps.cool_temperatures_colormap()

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'red')

        plot_proj = rtma_data.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        cs = ax.contourf(rtma_data.metpy.x, rtma_data.metpy.y, rtma_data, 
                         transform=rtma_data.metpy.cartopy_crs, levels=np.arange(-10, 33, 1), cmap=cmap, alpha=1, extend='min')


        cbar = fig.colorbar(cs, shrink=color_table_shrink, pad=colorbar_pad)
        cbar.set_label(label="Temperature (\N{DEGREE SIGN}F)", size=colorbar_label_font_size, fontweight='bold')


        plt.title("RTMA Current Frost & Freeze Areas (T <= 32\N{DEGREE SIGN}F)\n   Analysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_dry_and_windy_areas_based_on_sustained_winds(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_speed_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_font_size, signature_font_size, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind speed data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind speed data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Speed >= red_flag_warning_wind_speed_threshold (MPH). 
                                            5) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis for areas where the aforementioned "Dry and Windy" criteria are met. 
            

            Inputs:

                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_speed_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis showing current areas of dry and windy conditions. 
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap = colormaps.red_flag_warning_criteria_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_speed_threshold = red_flag_warning_wind_speed_threshold

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'violet')

        rtma_rh, rtma_wind, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_speed(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_wind = rtma_wind * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_wind >= red_flag_warning_wind_speed_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj = mask.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        # Plot the mask
        try:
            ax.pcolormesh(lon,lat,mask,transform=ccrs.PlateCarree(),cmap=cmap, zorder=2)

        except Exception as e:
            pass
            

        plt.title("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Wind Speed >= " + str(red_flag_warning_wind_speed_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_dry_and_windy_areas_based_on_wind_gusts(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_gust_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_font_size, signature_font_size, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind speed data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind speed data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Speed >= red_flag_warning_wind_speed_threshold (MPH). 
                                            5) Plots the 2.5km x 2.5km Real Time Mesoscale Analysis for areas where the aforementioned "Dry and Windy" criteria are met. 
            

            Inputs:

                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_speed_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure of the plotted 2.5km x 2.5km Real Time Mesoscale Analysis showing current areas of dry and windy conditions. 
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap = colormaps.red_flag_warning_criteria_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_gust_threshold = red_flag_warning_wind_gust_threshold

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'violet')

        rtma_rh, rtma_gust, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_gust(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_gust = rtma_gust * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_gust >= red_flag_warning_wind_gust_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj = mask.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')

        ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
        ax.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax.add_feature(GACC, linewidth=2.5, zorder=5)
        ax.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax.add_feature(PSAs, linewidth=1.5, zorder=4)

        # Plot the mask
        try:
            ax.pcolormesh(lon,lat,mask,transform=ccrs.PlateCarree(),cmap=cmap, zorder=2)

        except Exception as e:
            pass
            

        plt.title("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Wind Gust >= " + str(red_flag_warning_wind_gust_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=title_font_size, fontweight='bold')
        
        ax.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax.transAxes)

        return fig


    def plot_dry_and_windy_areas_based_on_sustained_winds_3_panel(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_speed_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, plot_title_font_size, subplot_title_font_size, colorbar_shrink, colorbar_pad, colorbar_label_font_size, signature_x_position, signature_y_position, signature_font_size, first_subplot_aspect_ratio, subsequent_subplot_aspect_ratio, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind speed data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind speed data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Speed >= red_flag_warning_wind_speed_threshold (MPH). 
                                            5) Plots a figure that consists of 3 subplots.
                                            List of subplots:
                                                        1) Plot where the dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_speed_threshold (MPH)
                                             
            

            Inputs:


                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_speed_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed.

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) color_table_shrink (Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                19) subplot_title_font_size (Integer) - Fontsize of all subplot titles. 
                
                20) first_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the first subplot. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size. 
                
                21) subsequent_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the second, third and fourth subplots. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size.

                22) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                23) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure showing the four aforementioned subplots:                                                             
                                                        1) Plot where the hot, dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_speed_threshold (MPH)
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap_rfw = colormaps.red_flag_warning_criteria_colormap()
        cmap_rh = colormaps.low_relative_humidity_colormap()
        cmap_wind = colormaps.red_flag_warning_wind_parameter_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_speed_threshold = red_flag_warning_wind_speed_threshold

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'violet')

        rtma_rh, rtma_wind, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_speed(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_wind = rtma_wind * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_wind >= red_flag_warning_wind_speed_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj_1 = mask.metpy.cartopy_crs
        plot_proj_2 = rtma_rh.metpy.cartopy_crs
        plot_proj_3 = rtma_wind.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')
        gs = gridspec.GridSpec(1, 9)
        ax0 = fig.add_subplot(gs[0:1, 0:3], projection=plot_proj_1)
        ax0.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax0.add_feature(GACC, linewidth=2.5, zorder=5)
        ax0.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax0.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax0.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax0.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax0.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax0.set_aspect(first_subplot_aspect_ratio)
        ax0.set_title("Exceptionally Dry & Windy Areas", fontsize=subplot_title_font_size, fontweight='bold')

        # Plot the mask
        try:
            ax0.pcolormesh(lon,lat,mask, transform=ccrs.PlateCarree(),cmap=cmap_rfw, zorder=2)

        except Exception as e:
            pass


        ax1 = fig.add_subplot(gs[0:1, 3:6], projection=plot_proj_2)
        ax1.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax1.add_feature(GACC, linewidth=2.5, zorder=5)
        ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax1.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax1.set_aspect(subsequent_subplot_aspect_ratio)
        ax1.set_title("Low Relative Humidity Areas", fontsize=subplot_title_font_size, fontweight='bold')

        cs_rh = ax1.contourf(rtma_rh.metpy.x, rtma_rh.metpy.y, rtma_rh, 
                         transform=rtma_rh.metpy.cartopy_crs, levels=np.arange(0, 16, 1), cmap=cmap_rh, alpha=1)

        cbar_rh = fig.colorbar(cs_rh, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_rh.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')


        ax2 = fig.add_subplot(gs[0:1, 6:9], projection=plot_proj_3)
        ax2.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax2.add_feature(GACC, linewidth=2.5, zorder=5)
        ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax2.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax2.set_aspect(subsequent_subplot_aspect_ratio)
        ax2.set_title("Sustained Wind Speed", fontsize=subplot_title_font_size, fontweight='bold')

        cs_wind = ax2.contourf(rtma_wind.metpy.x, rtma_wind.metpy.y, rtma_wind, 
                         transform=rtma_wind.metpy.cartopy_crs, levels=np.arange(25, 75, 5), cmap=cmap_wind, alpha=1)

        cbar_wind = fig.colorbar(cs_wind, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_wind.set_label(label="Sustained Wind Speed (MPH)", size=colorbar_label_font_size, fontweight='bold')   
        

        fig.suptitle("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Sustained Wind Speed >= " + str(red_flag_warning_wind_speed_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=plot_title_font_size, fontweight='bold')
        
        ax0.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy\n(C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax0.transAxes)

        return fig 


    def plot_dry_and_windy_areas_based_on_wind_gusts_3_panel(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_gust_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, plot_title_font_size, subplot_title_font_size, colorbar_shrink, colorbar_pad, colorbar_label_font_size, signature_x_position, signature_y_position, signature_font_size, first_subplot_aspect_ratio, subsequent_subplot_aspect_ratio, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind gust data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind gust data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Gust >= red_flag_warning_wind_gust_threshold (MPH). 
                                            5) Plots a figure that consists of 3 subplots.
                                            List of subplots:
                                                        1) Plot where the dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_gust_threshold (MPH)
                                             
            

            Inputs:


                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_gust_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed using wind gusts. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) color_table_shrink (Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                19) subplot_title_font_size (Integer) - Fontsize of all subplot titles. 
                
                20) first_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the first subplot. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size. 
                
                21) subsequent_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the second, third and fourth subplots. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size.

                22) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot.

                23) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure showing the four aforementioned subplots:                                                             
                                                        1) Plot where the hot, dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_speed_threshold (MPH)
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap_rfw = colormaps.red_flag_warning_criteria_colormap()
        cmap_rh = colormaps.low_relative_humidity_colormap()
        cmap_wind = colormaps.red_flag_warning_wind_parameter_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_gust_threshold = red_flag_warning_wind_gust_threshold

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'violet')

        rtma_rh, rtma_wind, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_gust(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_wind = rtma_wind * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_wind >= red_flag_warning_wind_gust_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj_1 = mask.metpy.cartopy_crs
        plot_proj_2 = rtma_rh.metpy.cartopy_crs
        plot_proj_3 = rtma_wind.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')
        gs = gridspec.GridSpec(1, 9)
        ax0 = fig.add_subplot(gs[0:1, 0:3], projection=plot_proj_1)
        ax0.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax0.add_feature(GACC, linewidth=2.5, zorder=5)
        ax0.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax0.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax0.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax0.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax0.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax0.set_aspect(first_subplot_aspect_ratio)
        ax0.set_title("Exceptionally Dry & Windy Areas", fontsize=subplot_title_font_size, fontweight='bold')

        # Plot the mask
        try:
            ax0.pcolormesh(lon,lat,mask, transform=ccrs.PlateCarree(),cmap=cmap_rfw, zorder=2)

        except Exception as e:
            pass


        ax1 = fig.add_subplot(gs[0:1, 3:6], projection=plot_proj_2)
        ax1.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax1.add_feature(GACC, linewidth=2.5, zorder=5)
        ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax1.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax1.set_aspect(subsequent_subplot_aspect_ratio)
        ax1.set_title("Low Relative Humidity Areas", fontsize=subplot_title_font_size, fontweight='bold')

        cs_rh = ax1.contourf(rtma_rh.metpy.x, rtma_rh.metpy.y, rtma_rh, 
                         transform=rtma_rh.metpy.cartopy_crs, levels=np.arange(0, 16, 1), cmap=cmap_rh, alpha=1)

        cbar_rh = fig.colorbar(cs_rh, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_rh.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')


        ax2 = fig.add_subplot(gs[0:1, 6:9], projection=plot_proj_3)
        ax2.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax2.add_feature(GACC, linewidth=2.5, zorder=5)
        ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax2.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax2.set_aspect(subsequent_subplot_aspect_ratio)
        ax2.set_title("Wind Gust", fontsize=subplot_title_font_size, fontweight='bold')

        cs_wind = ax2.contourf(rtma_wind.metpy.x, rtma_wind.metpy.y, rtma_wind, 
                         transform=rtma_wind.metpy.cartopy_crs, levels=np.arange(25, 75, 5), cmap=cmap_wind, alpha=1)

        cbar_wind = fig.colorbar(cs_wind, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_wind.set_label(label="Wind Gust (MPH)", size=colorbar_label_font_size, fontweight='bold')   
        

        fig.suptitle("RTMA Exceptionally Dry & Windy Areas (Shaded)\nRH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Wind Gust >= " + str(red_flag_warning_wind_gust_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=plot_title_font_size, fontweight='bold')
        
        ax0.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy\n(C) Eric J. Drewitz 2024\nData Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax0.transAxes)

        return fig

    def plot_dry_and_windy_areas_based_on_wind_gusts_3_panel_compact_view(red_flag_warning_relative_humidity_threshold, red_flag_warning_wind_gust_threshold, western_bound, eastern_bound, southern_bound, northern_bound, central_longitude, central_latitude, first_standard_parallel, second_standard_parallel, fig_x_length, fig_y_length, plot_title_font_size, subplot_1_title_font_size, subplot_2_and_3_title_font_size, colorbar_shrink, colorbar_pad, colorbar_label_font_size, signature_x_position, signature_y_position, signature_font_size, first_subplot_aspect_ratio, subsequent_subplot_aspect_ratio, show_rivers):

        r'''
            This function does the following:
                                            1) Downloads the latest available temperature, dewpoint, and wind gust data arrays. 
                                            2) Uses MetPy to calculate a relative humidity data array from the temperature and dewpoint data arrays. 
                                            3) Converts the wind gust data array from m/s to MPH. 
                                            4) Masks all areas where the following criteria is not met: RH <= red_flag_warning_relative_humidity_threshold (%) and Wind Gust >= red_flag_warning_wind_gust_threshold (MPH). 
                                            5) Plots a figure that consists of 3 subplots.
                                            List of subplots:
                                                        1) Plot where the dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_gust_threshold (MPH)
                                             
            

            Inputs:


                1) red_flag_warning_relative_humidity_threshold (Integer) - The National Weather Service Red Flag Warning threshold for relative humidity. 
                
                2) red_flag_warning_wind_gust_threshold (Integer) - The National Weather Service Red Flag Warning threshold for wind speed using wind gusts. 

                3) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

                4) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

                5) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

                6) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

                7) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

                8) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

                9) first_standard_parallel (Integer or Float) - Southern standard parallel. 

                10) second_standard_parallel (Integer or Float) - Northern standard parallel. 

                11) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

                12) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

                13) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 

                14) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.

                15) title_font_size (Integer) - The fontsize of the title of the figure. 

                16) signature_font_size (Integer) - The fontsize of the signature of the figure. 

                17) colorbar_label_font_size (Integer) - The fontsize of the title of the colorbar of the figure. 

                18) color_table_shrink (Float) - The size of the color bar with respect to the size of the figure. Generally this ranges between 0 and 1. Values closer to 0 correspond to shrinking the size of the color bar while larger values correspond to increasing the size of the color bar. 

                19) subplot_1_title_font_size (Integer) - Fontsize of the primary subplot titles. 

                20) subplot_2_and_3_title_font_size (Integer) - Fontsizes of the two secondary subplot titles. 
                
                21) first_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the first subplot. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size. 
                
                22) subsequent_subplot_aspect_ratio (Integer or Float) - The width to height ratio of the second, third and fourth subplots. When some subplots have colorbars while others do not in the same figure, this needs to be edited so all subplots appear to have the same size.

                23) colorbar_pad (Float) - This determines how close the position of the colorbar is to the edge of the subplot of the figure. 
                                           Default setting is 0.05.
                                           Lower numbers mean the colorbar is closer to the edge of the subplot while larger numbers allows for more space between the edge of the subplot and the colorbar.
                                           Example: If colorbar_pad = 0.00, then the colorbar is right up against the edge of the subplot. 

                24) show_rivers (Boolean) - If set to True, rivers will display on the map. If set to False, rivers 
                                            will not display on the map. 


            Returns:
                    1) A figure showing the four aforementioned subplots:                                                             
                                                        1) Plot where the hot, dry and windy conditions are located. 
                                                        2) Plot the relative humidity filtered only showing areas where the RH <= red_flag_warning_relative_humidity_threshold (%)
                                                        3) Plot the wind speed filtered only showing areas where Wind Speed >= red_flag_warning_wind_speed_threshold (MPH)
        
        '''

        local_time, utc_time = standard.plot_creation_time()

        cmap_rfw = colormaps.red_flag_warning_criteria_colormap()
        cmap_rh = colormaps.low_relative_humidity_colormap()
        cmap_wind = colormaps.red_flag_warning_wind_parameter_colormap()

        red_flag_warning_relative_humidity_threshold = red_flag_warning_relative_humidity_threshold

        red_flag_warning_wind_gust_threshold = red_flag_warning_wind_gust_threshold

        PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
        GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'violet')

        rtma_rh, rtma_wind, rtma_time = da.UCAR_THREDDS_SERVER_OPENDAP_Downloads.CONUS.get_red_flag_warning_parameters_using_wind_gust(utc_time)

        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        rtma_time = rtma_time.replace(tzinfo=from_zone)
        rtma_time = rtma_time.astimezone(to_zone)
        rtma_time_utc = rtma_time.astimezone(from_zone)

        rtma_wind = rtma_wind * 2.23694
        
        mapcrs = ccrs.LambertConformal(central_longitude=central_longitude, central_latitude=central_latitude, standard_parallels=(first_standard_parallel,second_standard_parallel))
        datacrs = ccrs.PlateCarree()


        mask = (rtma_rh <= red_flag_warning_relative_humidity_threshold) & (rtma_wind >= red_flag_warning_wind_gust_threshold)
        lon = mask['longitude']
        lat = mask['latitude']

        plot_proj_1 = mask.metpy.cartopy_crs
        plot_proj_2 = rtma_rh.metpy.cartopy_crs
        plot_proj_3 = rtma_wind.metpy.cartopy_crs

        fig = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig.set_facecolor('aliceblue')
        gs = gridspec.GridSpec(2, 9)
        ax0 = fig.add_subplot(gs[0:2, 0:6], projection=plot_proj_1)
        ax0.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax0.add_feature(GACC, linewidth=2.5, zorder=5)
        ax0.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax0.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax0.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax0.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax0.set_aspect(first_subplot_aspect_ratio)
        ax0.set_title("Exceptionally Dry & Windy Areas", fontsize=subplot_1_title_font_size, fontweight='bold')

        # Plot the mask
        try:
            ax0.pcolormesh(lon,lat,mask, transform=ccrs.PlateCarree(),cmap=cmap_rfw, zorder=2)

        except Exception as e:
            pass


        ax1 = fig.add_subplot(gs[0:1, 5:12], projection=plot_proj_2)
        ax1.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax1.add_feature(GACC, linewidth=2.5, zorder=5)
        ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax1.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax1.set_aspect(subsequent_subplot_aspect_ratio)
        ax1.set_title("Low Relative Humidity Areas", fontsize=subplot_2_and_3_title_font_size, fontweight='bold')

        cs_rh = ax1.contourf(rtma_rh.metpy.x, rtma_rh.metpy.y, rtma_rh, 
                         transform=rtma_rh.metpy.cartopy_crs, levels=np.arange(0, 16, 1), cmap=cmap_rh, alpha=1)

        cbar_rh = fig.colorbar(cs_rh, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_rh.set_label(label="Relative Humidity (%)", size=colorbar_label_font_size, fontweight='bold')


        ax2 = fig.add_subplot(gs[1:2, 5:12], projection=plot_proj_3)
        ax2.set_extent((western_bound, eastern_bound, southern_bound, northern_bound), crs=ccrs.PlateCarree())
        ax2.add_feature(GACC, linewidth=2.5, zorder=5)
        ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        ax2.add_feature(PSAs, linewidth=1.5, zorder=4)
        if show_rivers == True:
            ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        else:
            pass
        ax2.set_aspect(subsequent_subplot_aspect_ratio)
        ax2.set_title("Wind Gust", fontsize=subplot_2_and_3_title_font_size, fontweight='bold')

        cs_wind = ax2.contourf(rtma_wind.metpy.x, rtma_wind.metpy.y, rtma_wind, 
                         transform=rtma_wind.metpy.cartopy_crs, levels=np.arange(25, 75, 10), cmap=cmap_wind, alpha=1)

        cbar_wind = fig.colorbar(cs_wind, shrink=colorbar_shrink, location='bottom', pad=colorbar_pad)
        cbar_wind.set_label(label="Wind Gust (MPH)", size=colorbar_label_font_size, fontweight='bold')   
        

        fig.suptitle("RTMA Exceptionally Dry & Windy Areas (Shaded)|RH <= " + str(red_flag_warning_relative_humidity_threshold) + "% & Wind Gust >= " + str(red_flag_warning_wind_gust_threshold) + " MPH\nAnalysis Valid: " + rtma_time.strftime('%m/%d/%Y %H:00 Local') + " (" + rtma_time_utc.strftime('%H:00 UTC')+ ")", fontsize=plot_title_font_size, fontweight='bold')
        
        ax0.text(signature_x_position, signature_y_position, "Plot Created With FireWxPy|(C) Eric J. Drewitz 2024|Data Source: thredds.ucar.edu\nImage Created: " + local_time.strftime('%m/%d/%Y %H:%M Local') + " (" + utc_time.strftime('%H:%M UTC')+")", fontsize=signature_font_size, fontweight='bold', horizontalalignment='center',
       verticalalignment='bottom', transform=ax0.transAxes)

        return fig
