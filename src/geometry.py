# THIS FILE CONTAINS FUNCTIONS THAT RETURN VARIOUS TYPES OF GEOMETRIES FOR PLOTTING
# PYTHON DEPENDENCIES:
# 1) MATPLOTLIB
# 2) CARTOPY
#
#  (C) METEOROLOGIST ERIC J. DREWITZ
#               USDA/USFS

###### IMPORTS ################
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

#### INFORMATION CLASS ####
# The information class returns helpful tips for when the user encounters errors

class info:

    def PSA_shape_file_error():
        error_msg = f"""
        
        WARNING: COULD NOT FIND FILE. PLEASE MAKE SURE YOU HAVE THE CORRECT FILE PATH. 

        ALSO, BE SURE TO HAVE ALL THE FILES AS FOLLOWS LOCATED IN THE SAME PLACE.
        THE FILES NEEDED IN THE SAME PLACE ARE NAMED AS FOLLOWS:

        National_PSA_Current.shp
        National_PSA_Current.shx
        National_PSA_Current.xml
        National_PSA_Current.cpg
        National_PSA_Current.dbf
        National_PSA_Current.prj

        WHEN DOWNLOADING THESE SHAPEFILES FROM NIFC'S WEBSITE: https://data-nifc.opendata.arcgis.com/datasets/e580f3fd4d644366b121676714d69c2d/explore

        THE XML FILE BY DEFAULT HAS A DIFFERENT NAME THAN THE REST. RENAME THE XML FILE TO MATCH ALL OF THE OTHERFILE NAMES

        THE FILE NAMES SHOULD BE CALLED: "National_PSA_Current".FILETYPE

        """
        return error_msg

### PREDICTIVE SERVICES AREAS ###
# The Predictive Services Areas class returns the geometries for the predictive services areas to be used in plotting
class Predictive_Services_Areas:

    def get_PSAs(line_color):

        r'''
        THIS FUNCTION RETURNS THE GEOMETRIES FOR THE PREDICTIVE SERVICES AREAS FOR PLOTTING.

        THIS FUNCTION IS TO BE USED IF THE USER WISHES TO STORE THEIR SHAPEFILES IN THE SAME FOLDER AS THE PYTHON SCRIPTS THEY WISH TO RUN.

        THE USER CUSTOMIZES THE COLOR FOR THE PSA BORDERS

        (C) METEOROLOGIST ERIC J. DREWITZ 2024

        '''

        fname = 'National_PSA_Current.shp'
        
        try:
            shape_feature = ShapelyFeature(Reader(fname).geometries(),
                                           ccrs.PlateCarree(), facecolor=(0,0,0,0), edgecolor=line_color)
        
            return shape_feature

        except Exception as a:
            error = info.PSA_shape_file_error()
            print(error)


    def get_PSAs_custom_file_path(file_path, line_color):

        r'''
        THIS FUNCTION RETURNS THE GEOMETRIES FOR THE PREDICTIVE SERVICES AREAS FOR PLOTTING.

        THIS FUNCTION IS TO BE USED IF THE USER WISHES TO STORE THEIR SHAPEFILES ELSEWHERE THAN WHERE THEIR PYTHON
        SCRIPTS RUN. 

        THE USER CUSTOMIZES THE COLOR FOR THE PSA BORDERS

        (C) METEOROLOGIST ERIC J. DREWITZ 2024

        '''
        
        
        try:
            shape_feature = ShapelyFeature(Reader(file_path).geometries(),
                                           ccrs.PlateCarree(), facecolor=(0,0,0,0), edgecolor=line_color)
        
            return shape_feature

        except Exception as a:
            error = info.PSA_shape_file_error()
            print(error)


    def get_GACC_Boundaries(line_color):

        r'''
        THIS FUNCTION RETURNS THE GEOMETRIES FOR THE GACC BOUNDARIES FOR PLOTTING.

        THIS FUNCTION IS TO BE USED IF THE USER WISHES TO STORE THEIR SHAPEFILES IN THE SAME FOLDER AS THE PYTHON SCRIPTS THEY WISH TO RUN.

        THE USER CUSTOMIZES THE COLOR FOR THE PSA BORDERS

        (C) METEOROLOGIST ERIC J. DREWITZ 2024

        '''

        fname = 'National_GACC_Current.shp'
        
        try:
            shape_feature = ShapelyFeature(Reader(fname).geometries(),
                                           ccrs.PlateCarree(), facecolor=(0,0,0,0), edgecolor=line_color)
        
            return shape_feature

        except Exception as a:
            error = info.PSA_shape_file_error()
            print(error)

    
    def get_GACC_Boundaries_custom_file_path(file_path, line_color):

        r'''
        THIS FUNCTION RETURNS THE GEOMETRIES FOR THE GACC BOUNDARIES FOR PLOTTING.

        THIS FUNCTION IS TO BE USED IF THE USER WISHES TO STORE THEIR SHAPEFILES ELSEWHERE THAN WHERE THEIR PYTHON
        SCRIPTS RUN. 

        THE USER CUSTOMIZES THE COLOR FOR THE PSA BORDERS

        (C) METEOROLOGIST ERIC J. DREWITZ 2024

        '''
        
        
        try:
            shape_feature = ShapelyFeature(Reader(file_path).geometries(),
                                           ccrs.PlateCarree(), facecolor=(0,0,0,0), edgecolor=line_color)
        
            return shape_feature

        except Exception as a:
            error = info.PSA_shape_file_error()
            print(error)
