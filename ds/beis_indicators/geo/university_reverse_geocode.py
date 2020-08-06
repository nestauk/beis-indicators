# Script to reverse geocode universities
from collections import defaultdict
import geopandas as gp
from io import StringIO, BytesIO
import json
import os
import pandas as pd 
import requests
from shapely.geometry import Point
from zipfile import ZipFile

import beis_indicators
project_dir = beis_indicators.project_dir

# from beis_indicators.geo.reverse_geocoder import *
from beis_indicators.utils.nuts_utils import NUTS_YEARS
from beis_indicators.utils.geo_utils import (load_nuts_regions, load_leps_regions, 
        reverse_geocode, coordinates_to_points)

# if 'shapefiles' not in os.listdir(f'{project_dir}/data/raw'):
#     os.mkdir(f'{project_dir}/data/raw/shapefiles')
# 
# 
# #Load the shapefile lookup
# with open(f'{project_dir}/data/aux/shapefile_urls.json','r') as infile:
#     shape_lookup = json.load(infile)

#Get all the shapefiles
# for name in shape_lookup.keys():
#     get_shape(name,path=f'{project_dir}/data/raw/shapefiles/')

# #University metadata
# uni_meta = pd.read_csv('http://learning-provider.data.ac.uk/data/learning-providers-plus.csv')
# #Reverse geocoding
# #We focus on the last 2 periods as those are the ones for which we have data
# rcs = [reverse_geocode(place_df=uni_meta,
#                         shape_name=shape_n,
#                         shape_file=shape_f,
#                         place_id='UKPRN',
#                         coord_names= ['LONGITUDE','LATITUDE'])['NUTS_ID'] for shape_n,shape_f in 
# zip(['nuts2_2013','nuts2_2016'],
#     ['NUTS_RG_01M_2013_4326_LEVL_2.shp.zip','NUTS_RG_01M_2016_4326_LEVL_2.shp.zip'])]
# 
# uni_nuts = pd.concat(rcs,axis=1)
# 
# uni_nuts.columns = ['nuts2_2013','nuts2_2016']
# 
# with open(f'{project_dir}/data/interim/uni_geos.json','w') as outfile:
#     json.dump(uni_nuts.to_dict(orient='index'),outfile)
# 
def get_uni_metadata():
    """get_uni_metadata
    Retrieves university address and location data from learning-provider.ac.uk
    and stores it.
    """
    uni_meta = pd.read_csv('http://learning-provider.data.ac.uk/data/learning-providers-plus.csv')
    uni_meta_dir = f'{project_dir}/data/raw/universities'
    if not os.path.isdir(uni_meta_dir):
        os.mkdir(uni_meta_dir)
    uni_meta.to_csv(f'{uni_meta_dir}/uni_metadata.csv', index=False)

def reverse_geocode_unis(uni_meta):
    """reverse_geocode_unis
    Codes universities into NUTS2, NUTS3 and LEP regions.

    Args:
        uni_meta (pd.DataFrame): Table of university metadata.
    """

    shapefile_dir = f'{project_dir}/data/raw/shapefiles'
    out_dir = f'{project_dir}/data/metadata/universities'
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    uni_meta = coordinates_to_points(uni_meta, 'LONGITUDE', 'LATITUDE')

    for level in [2, 3]:
        uni_nuts_regions = defaultdict(dict)
        for year in NUTS_YEARS:
            nuts = load_nuts_regions(year, shapefile_dir, level=level)
            joined = reverse_geocode(uni_meta, nuts, 'EPSG:4326')
            nuts_ver = f'nuts{level}_{year}'
            for uni_id, nuts_id in zip(joined['UKPRN'], joined['NUTS_ID']):
                uni_nuts_regions[uni_id][nuts_ver] = nuts_id

        with open(f'{project_dir}/data/interim/uni_nuts{level}_geos.json', 'w') as outfile:
            json.dump(uni_nuts_regions, outfile)
    # TODO
    # This doesn't work because LEP regions overlap meaning that a university 
    # can be within more than one boundary. We would probably need to store them
    # in records format to achieve this.
    uni_leps_regions = defaultdict(dict)
    for year in [2014, 2017]:
        leps = load_leps_regions(year, shapefile_dir)
        joined = reverse_geocode(uni_meta, leps, 'EPSG:4326')
        col = f'lep{str(year)[-2:]}cd'
        lep_ver = f'lep_{year}'
        for uni_id, lep_id in zip(joined['UKPRN'], joined[col]):
            uni_leps_regions[uni_id][lep_ver] = lep_id

    with open(f'{project_dir}/data/interim/uni_lep_geos.json', 'w') as outfile:
        json.dump(uni_leps_regions, outfile)

