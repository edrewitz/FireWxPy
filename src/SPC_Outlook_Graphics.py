'''
This file hosts the functions to plot the latest critical fire weather outlook and dry lightning forecast
from the NOAA Storm Prediction Center (SPC). 

This file has 2 classes which are based on the geographical reference perspective:

1) Counties_Perspective: Uses state and county boundaries. 
2) Predictive_Services_Areas_Perspective: Uses Geographic Area Coordination Center (GACC) and 
                                          Predictive Services Areas (PSAs) boundaries. 

This file was written by Meteorologist Eric J. Drewitz 

            (C) Meteorologist Eric J. Drewitz 
                        USDA/USFS

'''



import pytz
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import metpy.plots as mpplots
import numpy as np
import parsers
import data_access as da
import geometry
import colormaps
import standard
import settings

from metpy.plots import USCOUNTIES
from datetime import datetime, timedelta
from metpy.plots import colortables
from dateutil import tz



def plot_critical_fire_weather_risk_outlook(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=0.7, colorbar_pad=0.02, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, show_state_borders=True,  show_county_borders=True, show_gacc_borders=False, show_psa_borders=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', show_sample_points=True, sample_point_fontsize=10, alpha=0.5, directory_name='CONUS', file_path=None, data_array=None, count_short=None, count_extended=None, state='us', gacc_region=None):

    r'''
    This function plots the latest available NOAA/SPC Critical Fire Weather Risk Outlook. 

    Inputs: 1) directory_name (String) - File path on the NWS FTP server to the file being downloaded. 
               (example for Pacific Southwest the directory_name is: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/

            2) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            3) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            4) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            5) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            6) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            7) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            8) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            9) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            10) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            11) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 
            13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.
            14) key_x_position (Integer or Float) - The x-position of the colortable key. 

            15) key_y_position (Integer or Float) - The y-position of the colortable key. 

            16) subplot_title_fontsize (Integer) - The fontsize of the plot title. 

            17) signature_fontsize (Integer) - The fontsize of the signature. 

            18) key_fontsize (Integer) - The fontsize of the key. 

            19) show_counties (Boolean) - If set to True, county borders will display. If set to False, county borders will not display. 

            20) show_rivers (Boolean) - If set to True, rivers will display. If set to False, rivers will not display. 
            21) state_linewidth (Integer) - Width of the state borders. 

            22) county_linewidth (Integer) - Width of the county borders.

    Return: A list of figures for each forecast day. 
    '''


    local_time, utc_time = standard.plot_creation_time()
    grid_time_interval = 24
    
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    cmap = colormaps.SPC_Critical_Fire_Weather_Risk_Outlook_colormap()
        
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound

    else:
        pass

    if state == None and gacc_region == None:
    
        directory_name = settings.check_NDFD_directory_name(directory_name)

    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, mapcrs, datacrs = settings.get_state_data_and_coords(state, True, 'critical fire')

        x1, x2, x3, y = settings.get_colorbar_label_coords(state, 'critical fire')
        

    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, mapcrs, datacrs = settings.get_gacc_region_data_and_coords(gacc_region, True, 'critical fire')


    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
    GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'black')

    if file_path == None:

        try:

            grbs, ds, count_short, count_extended = da.FTP_Downloads.get_NWS_NDFD_7_Day_grid_data(directory_name, 'ds.critfireo.bin')

            print("Downloaded data successfully!")
        except Exception as a:

            print("Trying again to download data...")

            count_short, count_extended = da.FTP_Downloads.get_NWS_NDFD_7_Day_grid_data_test(directory_name, 'ds.critfireo.bin')
    
                
        grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, grb_6_vals, grb_6_start, grb_6_end, grb_7_vals, grb_7_start, grb_7_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5, lats_6, lons_6, lats_7, lons_7, count, count_short, count_extended, discard = parsers.NDFD.parse_GRIB_files_full_forecast_period('ds.critfireo.bin', 24, False, count_short, count_extended, directory_name)

    if file_path != None:

        grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, grb_6_vals, grb_6_start, grb_6_end, grb_7_vals, grb_7_start, grb_7_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5, lats_6, lons_6, lats_7, lons_7, count, count_short, count_extended, discard = parsers.NDFD.parse_GRIB_files_full_forecast_period(file_path, 24, False, count_short, count_extended, directory_name)

    try:
        if grb_7_vals.all() != None:
            test_7 = True

    except Exception as e:
        test_7 = False       

    grb_1_start = grb_1_start.replace(tzinfo=from_zone)
    grb_1_start = grb_1_start.astimezone(to_zone)
    grb_2_start = grb_2_start.replace(tzinfo=from_zone)
    grb_2_start = grb_2_start.astimezone(to_zone)
    grb_3_start = grb_3_start.replace(tzinfo=from_zone)
    grb_3_start = grb_3_start.astimezone(to_zone)
    grb_4_start = grb_4_start.replace(tzinfo=from_zone)
    grb_4_start = grb_4_start.astimezone(to_zone)
    grb_5_start = grb_5_start.replace(tzinfo=from_zone)
    grb_5_start = grb_5_start.astimezone(to_zone)
    grb_6_start = grb_6_start.replace(tzinfo=from_zone)
    grb_6_start = grb_6_start.astimezone(to_zone)

    grb_1_end = grb_1_end.replace(tzinfo=from_zone)
    grb_1_end = grb_1_end.astimezone(to_zone)
    grb_2_end = grb_2_end.replace(tzinfo=from_zone)
    grb_2_end = grb_2_end.astimezone(to_zone)
    grb_3_end = grb_3_end.replace(tzinfo=from_zone)
    grb_3_end = grb_3_end.astimezone(to_zone)
    grb_4_end = grb_4_end.replace(tzinfo=from_zone)
    grb_4_end = grb_4_end.astimezone(to_zone)
    grb_5_end = grb_5_end.replace(tzinfo=from_zone)
    grb_5_end = grb_5_end.astimezone(to_zone)
    grb_6_end = grb_6_end.replace(tzinfo=from_zone)
    grb_6_end = grb_6_end.astimezone(to_zone)
    
    if test_7 == True:
        grb_7_start = grb_7_start.replace(tzinfo=from_zone)
        grb_7_start = grb_7_start.astimezone(to_zone)

        grb_7_end = grb_7_end.replace(tzinfo=from_zone)
        grb_7_end = grb_7_end.astimezone(to_zone)
    else:
        pass   
        
    files = count

    
    figs = [] 

    fig1 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig1.set_facecolor('aliceblue')
    fig1.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')

    ax1 = fig1.add_subplot(1, 1, 1, projection=mapcrs)
    ax1.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax1.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax1.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax1.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax1.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax1.set_title('Critical Fire Wx Forecast (Day 1)\nStart: '+ grb_1_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_1_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs1 = ax1.contourf(lons_1, lats_1, grb_1_vals, levels=np.arange(4, 12, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar1 = fig1.colorbar(cs1, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar1.set_ticks([])

    fig1.text(x1, y,'ELEVATED', fontsize=13, fontweight='bold')
    fig1.text(x2, y,'CRITICAL', fontsize=13, fontweight='bold')
    fig1.text(x3, y,'EXTREME', fontsize=13, fontweight='bold')
    
    fig2 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig2.set_facecolor('aliceblue')
    fig2.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax2 = fig2.add_subplot(1, 1, 1, projection=mapcrs)
    ax2.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax2.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax2.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax2.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax2.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
        
    ax2.set_title('Critical Fire Wx Forecast (Day 2)\nStart: '+ grb_2_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_2_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs2 = ax2.contourf(lons_2, lats_2, grb_2_vals, levels=np.arange(4, 12, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar2 = fig2.colorbar(cs2, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar2.set_ticks([])

    fig2.text(x1, y,'ELEVATED', fontsize=13, fontweight='bold')
    fig2.text(x2, y,'CRITICAL', fontsize=13, fontweight='bold')
    fig2.text(x3, y,'EXTREME', fontsize=13, fontweight='bold')


    fig3 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig3.set_facecolor('aliceblue')
    fig3.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')

    ax3 = fig3.add_subplot(1, 1, 1, projection=mapcrs)
    ax3.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax3.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax3.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax3.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax3.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax3.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax3.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax3.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax3.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax3.set_title('Critical Fire Wx Forecast (Day 3)\nStart: '+ grb_3_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_3_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs3 = ax3.contourf(lons_3, lats_3, grb_3_vals, levels=np.arange(4, 12, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar3 = fig3.colorbar(cs3, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar3.set_ticks([])

    fig3.text(x1, y,'ELEVATED', fontsize=13, fontweight='bold')
    fig3.text(x2, y,'CRITICAL', fontsize=13, fontweight='bold')
    fig3.text(x3, y,'EXTREME', fontsize=13, fontweight='bold')
    
    fig4 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig4.set_facecolor('aliceblue')
    fig4.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax4 = fig4.add_subplot(1, 1, 1, projection=mapcrs)
    ax4.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax4.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax4.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax4.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax4.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax4.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax4.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax4.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax4.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax4.set_title('Critical Fire Wx Forecast (Day 4)\nStart: '+ grb_4_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_4_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs4 = ax4.contourf(lons_4, lats_4, grb_4_vals, levels=np.arange(4, 12, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar4 = fig4.colorbar(cs4, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar4.set_ticks([])

    fig4.text(x1, y,'ELEVATED', fontsize=13, fontweight='bold')
    fig4.text(x2, y,'CRITICAL', fontsize=13, fontweight='bold')
    fig4.text(x3, y,'EXTREME', fontsize=13, fontweight='bold')

    fig5 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig5.set_facecolor('aliceblue')
    fig5.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax5 = fig5.add_subplot(1, 1, 1, projection=mapcrs)
    ax5.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax5.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax5.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax5.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax5.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax5.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax5.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax5.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax5.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax5.set_title('Critical Fire Wx Forecast (Day 5)\nStart: '+ grb_5_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_5_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs5 = ax5.contourf(lons_5, lats_5, grb_5_vals, levels=np.arange(4, 12, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar5 = fig5.colorbar(cs5, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar5.set_ticks([])

    fig5.text(x1, y,'ELEVATED', fontsize=13, fontweight='bold')
    fig5.text(x2, y,'CRITICAL', fontsize=13, fontweight='bold')
    fig5.text(x3, y,'EXTREME', fontsize=13, fontweight='bold')

    fig6 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig6.set_facecolor('aliceblue')
    fig6.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax6 = fig6.add_subplot(1, 1, 1, projection=mapcrs)
    ax6.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax6.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax6.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax6.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax6.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax6.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax6.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax6.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax6.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax6.set_title('Critical Fire Wx Forecast (Day 6)\nStart: '+ grb_6_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_6_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs6 = ax6.contourf(lons_6, lats_6, grb_6_vals, levels=np.arange(4, 12, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar6 = fig6.colorbar(cs6, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar6.set_ticks([])

    fig6.text(x1, y,'ELEVATED', fontsize=13, fontweight='bold')
    fig6.text(x2, y,'CRITICAL', fontsize=13, fontweight='bold')
    fig6.text(x3, y,'EXTREME', fontsize=13, fontweight='bold')

    if test_7 == True:

        fig7 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig7.set_facecolor('aliceblue')
        fig7.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
        
        ax7 = fig7.add_subplot(1, 1, 1, projection=mapcrs)
        ax7.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax7.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax7.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax7.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax7.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        if show_gacc_borders == True:
            ax7.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
        else:
            pass
        if show_psa_borders == True:
            ax7.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
        else:
            pass
        if show_county_borders == True:
            ax7.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
        else:
            pass
        if show_state_borders == True:
            ax7.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
        else:
            pass
        ax7.set_title('Critical Fire Wx Forecast (Day 7)\nStart: '+ grb_7_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_7_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
            
        cs7 = ax7.contourf(lons_7, lats_7, grb_7_vals, levels=np.arange(4, 12, 2), cmap=cmap, transform=datacrs, zorder=2)

        cbar7 = fig7.colorbar(cs7, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
        cbar7.set_ticks([])
    
        fig7.text(x1, y,'ELEVATED', fontsize=13, fontweight='bold')
        fig7.text(x2, y,'CRITICAL', fontsize=13, fontweight='bold')
        fig7.text(x3, y,'EXTREME', fontsize=13, fontweight='bold')
    
        figs.append(fig1)
        figs.append(fig2)
        figs.append(fig3)
        figs.append(fig4)
        figs.append(fig5)
        figs.append(fig6)
        figs.append(fig7)

    else:
        figs.append(fig1)
        figs.append(fig2)
        figs.append(fig3)
        figs.append(fig4)
        figs.append(fig5)
        figs.append(fig6)

    return figs


def plot_dry_lightning_outlook(western_bound=None, eastern_bound=None, southern_bound=None, northern_bound=None, fig_x_length=None, fig_y_length=None, signature_x_position=None, signature_y_position=None, color_table_shrink=0.7, colorbar_pad=0.02, title_fontsize=12, subplot_title_fontsize=10, signature_fontsize=10, colorbar_fontsize=8, show_rivers=True, show_state_borders=True,  show_county_borders=True, show_gacc_borders=False, show_psa_borders=False, state_border_linewidth=2, county_border_linewidth=1, gacc_border_linewidth=2, psa_border_linewidth=1, state_border_linestyle='-', county_border_linestyle='-', gacc_border_linestyle='-', psa_border_linestyle='-', show_sample_points=True, sample_point_fontsize=10, alpha=0.5, directory_name='CONUS', file_path=None, data_array=None, count_short=None, count_extended=None, state='us', gacc_region=None):

    r'''
    This function plots the latest available NOAA/SPC Critical Fire Weather Risk Outlook. 

    Inputs: 1) directory_name (String) - File path on the NWS FTP server to the file being downloaded. 
               (example for Pacific Southwest the directory_name is: /SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/

            2) western_bound (Integer or Float) - Western extent of the plot in decimal degrees.

            3) eastern_bound (Integer or Float) - Eastern extent of the plot in decimal degrees.

            4) southern_bound (Integer or Float) - Southern extent of the plot in decimal degrees.

            5) northern_bound (Integer or Float) - Northern extent of the plot in decimal degrees.

            6) central_longitude (Integer or Float) - The central longitude. Defaults to -96.

            7) central_latitude (Integer or Float) - The central latitude. Defaults to 39.

            8) first_standard_parallel (Integer or Float) - Southern standard parallel. 

            9) second_standard_parallel (Integer or Float) - Northern standard parallel. 
            
            10) fig_x_length (Integer) - The horizontal (x-direction) length of the entire figure. 

            11) fig_y_length (Integer) - The vertical (y-direction) length of the entire figure. 

            12) signature_x_position (Integer or Float) - The x-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure. 
            13) signature_y_position (Integer or Float) - The y-position of the signature (The signature is where the credit is given to FireWxPy and the data source on the graphic) with respect to the axis of the subplot of the figure.
            14) key_x_position (Integer or Float) - The x-position of the colortable key. 

            15) key_y_position (Integer or Float) - The y-position of the colortable key. 

            16) subplot_title_fontsize (Integer) - The fontsize of the plot title. 

            17) signature_fontsize (Integer) - The fontsize of the signature. 

            18) key_fontsize (Integer) - The fontsize of the key. 

            19) show_counties (Boolean) - If set to True, county borders will display. If set to False, county borders will not display. 

            20) show_rivers (Boolean) - If set to True, rivers will display. If set to False, rivers will not display. 
            21) state_linewidth (Integer) - Width of the state borders. 

            22) county_linewidth (Integer) - Width of the county borders.

    Return: A list of figures for each forecast day. 
    '''


    local_time, utc_time = standard.plot_creation_time()
    grid_time_interval = 24
    
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    cmap = colormaps.SPC_Dry_Lightning_Risk_Outlook_colormap()
        
    mapcrs = ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    if western_bound != None and eastern_bound != None and southern_bound != None and northern_bound != None and fig_x_length != None and fig_y_length != None and signature_x_position != None and signature_y_position != None:

        fig_x_length = fig_x_length
        fig_y_length = fig_y_length
        signature_x_position = signature_x_position
        signature_y_position = signature_y_position
        western_bound = western_bound
        eastern_bound = eastern_bound
        southern_bound = southern_bound
        northern_bound = northern_bound

    else:
        pass

    if state == None and gacc_region == None:
    
        directory_name = settings.check_NDFD_directory_name(directory_name)

    if state != None and gacc_region == None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, mapcrs, datacrs = settings.get_state_data_and_coords(state, True, 'dry lightning')

        x1, x2, x3, y = settings.get_colorbar_label_coords(state, 'dry lightning')
        

    if state == None and gacc_region != None:
        directory_name, western_bound, eastern_bound, southern_bound, northern_bound, fig_x_length, fig_y_length, signature_x_position, signature_y_position, title_fontsize, subplot_title_fontsize, signature_fontsize, sample_point_fontsize, colorbar_fontsize, color_table_shrink, mapcrs, datacrs = settings.get_gacc_region_data_and_coords(gacc_region, True, 'dry lightning')


    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    PSAs = geometry.Predictive_Services_Areas.get_PSAs_custom_file_path(f"PSA Shapefiles/National_PSA_Current.shp", 'black')
    GACC = geometry.Predictive_Services_Areas.get_GACC_Boundaries_custom_file_path(f"GACC Boundaries Shapefiles/National_GACC_Current.shp", 'black')

    if file_path == None:

        try:

            grbs, ds, count_short, count_extended = da.FTP_Downloads.get_NWS_NDFD_7_Day_grid_data(directory_name, 'ds.dryfireo.bin')

            print("Downloaded data successfully!")
        except Exception as a:

            print("Trying again to download data...")

            count_short, count_extended = da.FTP_Downloads.get_NWS_NDFD_7_Day_grid_data_test(directory_name, 'ds.dryfireo.bin')
    
                
        grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, grb_6_vals, grb_6_start, grb_6_end, grb_7_vals, grb_7_start, grb_7_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5, lats_6, lons_6, lats_7, lons_7, count, count_short, count_extended, discard = parsers.NDFD.parse_GRIB_files_full_forecast_period('ds.dryfireo.bin', 24, False, count_short, count_extended, directory_name)

    if file_path != None:

        grb_1_vals, grb_1_start, grb_1_end, grb_2_vals, grb_2_start, grb_2_end, grb_3_vals, grb_3_start, grb_3_end, grb_4_vals, grb_4_start, grb_4_end, grb_5_vals, grb_5_start, grb_5_end, grb_6_vals, grb_6_start, grb_6_end, grb_7_vals, grb_7_start, grb_7_end, lats_1, lons_1, lats_2, lons_2, lats_3, lons_3, lats_4, lons_4, lats_5, lons_5, lats_6, lons_6, lats_7, lons_7, count, count_short, count_extended, discard = parsers.NDFD.parse_GRIB_files_full_forecast_period(file_path, 24, False, count_short, count_extended, directory_name)

    try:
        if grb_7_vals.all() != None:
            test_7 = True

    except Exception as e:
        test_7 = False       

    grb_1_start = grb_1_start.replace(tzinfo=from_zone)
    grb_1_start = grb_1_start.astimezone(to_zone)
    grb_2_start = grb_2_start.replace(tzinfo=from_zone)
    grb_2_start = grb_2_start.astimezone(to_zone)
    grb_3_start = grb_3_start.replace(tzinfo=from_zone)
    grb_3_start = grb_3_start.astimezone(to_zone)
    grb_4_start = grb_4_start.replace(tzinfo=from_zone)
    grb_4_start = grb_4_start.astimezone(to_zone)
    grb_5_start = grb_5_start.replace(tzinfo=from_zone)
    grb_5_start = grb_5_start.astimezone(to_zone)
    grb_6_start = grb_6_start.replace(tzinfo=from_zone)
    grb_6_start = grb_6_start.astimezone(to_zone)

    grb_1_end = grb_1_end.replace(tzinfo=from_zone)
    grb_1_end = grb_1_end.astimezone(to_zone)
    grb_2_end = grb_2_end.replace(tzinfo=from_zone)
    grb_2_end = grb_2_end.astimezone(to_zone)
    grb_3_end = grb_3_end.replace(tzinfo=from_zone)
    grb_3_end = grb_3_end.astimezone(to_zone)
    grb_4_end = grb_4_end.replace(tzinfo=from_zone)
    grb_4_end = grb_4_end.astimezone(to_zone)
    grb_5_end = grb_5_end.replace(tzinfo=from_zone)
    grb_5_end = grb_5_end.astimezone(to_zone)
    grb_6_end = grb_6_end.replace(tzinfo=from_zone)
    grb_6_end = grb_6_end.astimezone(to_zone)
    
    if test_7 == True:
        grb_7_start = grb_7_start.replace(tzinfo=from_zone)
        grb_7_start = grb_7_start.astimezone(to_zone)

        grb_7_end = grb_7_end.replace(tzinfo=from_zone)
        grb_7_end = grb_7_end.astimezone(to_zone)
    else:
        pass   
        
    files = count

    
    figs = [] 

    fig1 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig1.set_facecolor('aliceblue')
    fig1.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')

    ax1 = fig1.add_subplot(1, 1, 1, projection=mapcrs)
    ax1.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax1.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax1.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax1.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax1.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax1.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax1.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax1.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax1.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax1.set_title('Dry Lightning Forecast (Day 1)\nStart: '+ grb_1_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_1_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs1 = ax1.contourf(lons_1, lats_1, grb_1_vals, levels=np.arange(4, 10, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar1 = fig1.colorbar(cs1, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar1.set_ticks([])

    fig1.text(x1, y,'ISOLATED', fontsize=13, fontweight='bold')
    fig1.text(x2, y,'SCATTERED', fontsize=13, fontweight='bold')
    
    fig2 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig2.set_facecolor('aliceblue')
    fig2.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax2 = fig2.add_subplot(1, 1, 1, projection=mapcrs)
    ax2.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax2.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax2.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax2.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax2.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax2.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax2.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax2.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax2.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
        
    ax2.set_title('Dry Lightning Forecast (Day 2)\nStart: '+ grb_2_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_2_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs2 = ax2.contourf(lons_2, lats_2, grb_2_vals, levels=np.arange(4, 10, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar2 = fig2.colorbar(cs2, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar2.set_ticks([])

    fig2.text(x1, y,'ISOLATED', fontsize=13, fontweight='bold')
    fig2.text(x2, y,'SCATTERED', fontsize=13, fontweight='bold')

    fig3 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig3.set_facecolor('aliceblue')
    fig3.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')

    ax3 = fig3.add_subplot(1, 1, 1, projection=mapcrs)
    ax3.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax3.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax3.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax3.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax3.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax3.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax3.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax3.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax3.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax3.set_title('Dry Lightning Forecast (Day 3)\nStart: '+ grb_3_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_3_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs3 = ax3.contourf(lons_3, lats_3, grb_3_vals, levels=np.arange(4, 10, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar3 = fig3.colorbar(cs3, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar3.set_ticks([])

    fig3.text(x1, y,'ISOLATED', fontsize=13, fontweight='bold')
    fig3.text(x2, y,'SCATTERED', fontsize=13, fontweight='bold')
    
    fig4 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig4.set_facecolor('aliceblue')
    fig4.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax4 = fig4.add_subplot(1, 1, 1, projection=mapcrs)
    ax4.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax4.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax4.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax4.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax4.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax4.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax4.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax4.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax4.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax4.set_title('Dry Lightning Forecast (Day 4)\nStart: '+ grb_4_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_4_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs4 = ax4.contourf(lons_4, lats_4, grb_4_vals, levels=np.arange(4, 10, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar4 = fig4.colorbar(cs4, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar4.set_ticks([])

    fig4.text(x1, y,'ISOLATED', fontsize=13, fontweight='bold')
    fig4.text(x2, y,'SCATTERED', fontsize=13, fontweight='bold')

    fig5 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig5.set_facecolor('aliceblue')
    fig5.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax5 = fig5.add_subplot(1, 1, 1, projection=mapcrs)
    ax5.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax5.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax5.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax5.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax5.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax5.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax5.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax5.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax5.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax5.set_title('Dry Lightning Forecast (Day 5)\nStart: '+ grb_5_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_5_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs5 = ax5.contourf(lons_5, lats_5, grb_5_vals, levels=np.arange(4, 10, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar5 = fig5.colorbar(cs5, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar5.set_ticks([])

    fig5.text(x1, y,'ISOLATED', fontsize=13, fontweight='bold')
    fig5.text(x2, y,'SCATTERED', fontsize=13, fontweight='bold')

    fig6 = plt.figure(figsize=(fig_x_length, fig_y_length))
    fig6.set_facecolor('aliceblue')
    fig6.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
    
    ax6 = fig6.add_subplot(1, 1, 1, projection=mapcrs)
    ax6.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
    ax6.add_feature(cfeature.LAND, color='beige', zorder=1)
    ax6.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
    ax6.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
    if show_rivers == True:
        ax6.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
    if show_gacc_borders == True:
        ax6.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
    else:
        pass
    if show_psa_borders == True:
        ax6.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
    else:
        pass
    if show_county_borders == True:
        ax6.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
    else:
        pass
    if show_state_borders == True:
        ax6.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
    else:
        pass
    ax6.set_title('Dry Lightning Forecast (Day 6)\nStart: '+ grb_6_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_6_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
        
    cs6 = ax6.contourf(lons_6, lats_6, grb_6_vals, levels=np.arange(4, 10, 2), cmap=cmap, transform=datacrs, zorder=2)

    cbar6 = fig6.colorbar(cs6, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
    cbar6.set_ticks([])

    fig6.text(x1, y,'ISOLATED', fontsize=13, fontweight='bold')
    fig6.text(x2, y,'SCATTERED', fontsize=13, fontweight='bold')

    if test_7 == True:

        fig7 = plt.figure(figsize=(fig_x_length, fig_y_length))
        fig7.set_facecolor('aliceblue')
        fig7.text(signature_x_position, signature_y_position, '                Plot Created With FireWxPy (C) Eric J. Drewitz 2024\nData Source: NOAA/NWS/SPC | Image Created: ' + utc_time.strftime('%a %m/%d/%Y %H:%MZ'), fontsize=signature_fontsize, fontweight='bold')
        
        ax7 = fig7.add_subplot(1, 1, 1, projection=mapcrs)
        ax7.set_extent([western_bound, eastern_bound, southern_bound, northern_bound], datacrs)
        ax7.add_feature(cfeature.LAND, color='beige', zorder=1)
        ax7.add_feature(cfeature.OCEAN, color='lightcyan', zorder=3)
        ax7.add_feature(cfeature.LAKES, color='lightcyan', zorder=3)
        if show_rivers == True:
            ax7.add_feature(cfeature.RIVERS, color='lightcyan', zorder=3)
        if show_gacc_borders == True:
            ax7.add_feature(GACC, linewidth=gacc_border_linewidth, linestyle=gacc_border_linestyle, zorder=6)
        else:
            pass
        if show_psa_borders == True:
            ax7.add_feature(PSAs, linewidth=psa_border_linewidth, linestyle=psa_border_linestyle, zorder=5)
        else:
            pass
        if show_county_borders == True:
            ax7.add_feature(USCOUNTIES, linewidth=county_border_linewidth, linestyle=county_border_linestyle, zorder=5)
        else:
            pass
        if show_state_borders == True:
            ax7.add_feature(cfeature.STATES, linewidth=state_border_linewidth, linestyle=state_border_linestyle, edgecolor='black', zorder=6)
        else:
            pass
        ax7.set_title('Dry Lightning Forecast (Day 7)\nStart: '+ grb_7_start.strftime('%a %m/%d %H:00 Local') + ' | End: '+ grb_7_end.strftime('%a %m/%d %H:00 Local'), fontsize=subplot_title_fontsize, fontweight='bold', loc='center')
            
        cs7 = ax7.contourf(lons_7, lats_7, grb_7_vals, levels=np.arange(4, 10, 2), cmap=cmap, transform=datacrs, zorder=2)

        cbar7 = fig7.colorbar(cs7, location='bottom', shrink=color_table_shrink, pad=colorbar_pad)
        cbar7.set_ticks([])
    
        fig7.text(x1, y,'ISOLATED', fontsize=13, fontweight='bold')
        fig7.text(x2, y,'SCATTERED', fontsize=13, fontweight='bold')
    
        figs.append(fig1)
        figs.append(fig2)
        figs.append(fig3)
        figs.append(fig4)
        figs.append(fig5)
        figs.append(fig6)
        figs.append(fig7)

    else:
        figs.append(fig1)
        figs.append(fig2)
        figs.append(fig3)
        figs.append(fig4)
        figs.append(fig5)
        figs.append(fig6)

    return figs

