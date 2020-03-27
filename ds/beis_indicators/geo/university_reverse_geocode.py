# Script to reverse geocode universities
import os
import requests
from io import StringIO, BytesIO
from zipfile import ZipFile
import json
import geopandas as gp
from shapely.geometry import Point
import pandas as pd 

import beis_indicators
project_dir = beis_indicators.project_dir
#Import the functions for reverse geocoding
from beis_indicators.geo.reverse_geocoder import *

if 'shapefiles' not in os.listdir(f'{project_dir}/data/raw'):
    os.mkdir(f'{project_dir}/data/raw/shapefiles')


#Load the shapefile lookup
with open(f'{project_dir}/data/aux/shapefile_urls.json','r') as infile:
    shape_lookup = json.load(infile)

#Get all the shapefiles
for name in shape_lookup.keys():
    get_shape(name,path=f'{project_dir}/data/raw/shapefiles/')

#University metadata
uni_meta = pd.read_csv('http://learning-provider.data.ac.uk/data/learning-providers-plus.csv')
#Reverse geocoding
#We focus on the last 2 periods as those are the ones for which we have data
rcs = [reverse_geocode(place_df=uni_meta,
                        shape_name=shape_n,
                        shape_file=shape_f,
                        place_id='UKPRN',
                        coord_names= ['LONGITUDE','LATITUDE'])['NUTS_ID'] for shape_n,shape_f in 
zip(['nuts2_2013','nuts2_2016'],
    ['NUTS_RG_01M_2013_4326_LEVL_2.shp.zip','NUTS_RG_01M_2016_4326_LEVL_2.shp.zip'])]

uni_nuts = pd.concat(rcs,axis=1)

uni_nuts.columns = ['nuts2_2013','nuts2_2016']

with open(f'{project_dir}/data/interim/uni_geos.json','w') as outfile:
    json.dump(uni_nuts.to_dict(orient='index'),outfile)


