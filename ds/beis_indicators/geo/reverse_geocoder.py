import os
import requests
import geopandas as gp
import pandas as pd 
from zipfile import ZipFile
import beis_indicators
import json
from io import StringIO, BytesIO
from shapely.geometry import Point

import beis_indicators
project_dir = beis_indicators.project_dir

#Load the shapefile lookup
with open(f'{project_dir}/data/aux/shapefile_urls.json','r') as infile:
    shape_lookup = json.load(infile)


def get_shape(file_name,path):
    '''
    Utility function to extract and the shapefile
    
    Arguments:
        url: url for the shapefile zip
        file_name: name of the file where we want to extract the data
    
    '''

    #Do we need to get the data or is it already there?

    shape_names = os.listdir(f'{project_dir}/data/raw/shapefiles')

    if file_name not in shape_names:

        #Get the data
        print(f'getting {file_name}...')

        #Get url
        url = shape_lookup[file_name]

        #Request data
        req = requests.get(url)
        
        #Parse the content
        z = ZipFile(BytesIO(req.content))
        
        #Save
        print(f'saving {file_name}...')
        z.extractall(f'{path}{file_name}')

    else:
        print(f'{file_name} already collected')


def reverse_geocode(place_df,shape_name,
                     shape_file,
                     place_id,
                     coord_names= ['longitude','latitude']):
    '''
    The reverse geocoder takes a df with geographical coordinates and does a spatial merge with a shapefile.
    
    Args:
        place_df (df). A dataframe where every row is an entity we want to reverse geocode
        shape_name (str): The name of the shapefile we used
        shape_file (str) the name of the actual shapefile.
        place_id (str): the name of the variable with the place id in place dfs
        coord_names (list): Names for the lon and lat variables in the place_df
        
    Returns:
        A spatially merged df with the location ids and their 
    
    
    '''
    
    #Read the shapefile    
    print('Reading shapefile...')
    
    source = f'{project_dir}/data/raw/shapefiles/{shape_name}/{shape_file}'
    
    #Do we need to unzip it? 
    #This will be the case with the eurostat files
    if 'zip' in shape_file.lower():
        
    
        #Here we are removing the .shp.zip 
        target = f'{project_dir}/data/raw/shapefiles/{shape_name}/{shape_file}'.split('.')[0]
        
        with ZipFile(source,'r') as infile:
                infile.extractall(target)
        
        #Get the shapefile name
        sh = [x for x in os.listdir(target) if '.shp' in x.lower()][0]
        
        shape = gp.read_file(f'{target}/{sh}')
              
    else:
        shape = gp.read_file(f'{target}/{sh}')
        
              
    
    #Change its projection so it can deal with lats and lons
    shape = shape.to_crs("EPSG:4326")
    
    
    #Create a place_holder df (ho ho) where the index is the place id
    place_holder = gp.GeoDataFrame(index=place_df[place_id],crs="EPSG:4326")
    
    #Create the geo field for spatial merge using Point
    place_holder['geometry'] = [Point(x[coord_names[0]],x[coord_names[1]]) for rid,x in place_df.iterrows()]
    
    print('Joining...')
    
    #Spatial join: looks for points inside the polygons
    joined = gp.sjoin(place_holder,shape,op='within')
    
    #Return the joined df
    return(joined)

#get_shape('nuts2_2010',f'{project_dir}/data/shapefiles/')

