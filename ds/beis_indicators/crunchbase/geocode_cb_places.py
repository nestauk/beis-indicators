import os
import re
import json
from data_getters.labs.core import download_file
from data_getters.core import get_engine
from ast import literal_eval
import pandas as pd

import beis_indicators
from beis_indicators.geo.reverse_geocoder import reverse_geocode
from beis_indicators.utils.dir_file_management import *
from beis_indicators.utils.nesta_utils import get_daps_data
from dotenv import load_dotenv

project_dir = beis_indicators.project_dir

#Get config path to work with daps data
load_dotenv()

conf_path = os.environ.get('config_path')

def get_daps_data(table,connection,chunksize=1000):
    '''
    Utility function to get data from DAPS with less faff
    
    Args:
        -table is the SQL table in DAPS that we are extracting
        -connection is the database connection we are using
        -Chunksize are the chunks to download
    
    Returns:
        -A dataframe with the data we have collected
    
    '''
    #Get chunks
    chunks = pd.read_sql_table(table, connection, chunksize=chunksize)
    
    #Create df
    df = pd.concat(chunks)
    
    #Return data
    return(df)

# Download CrunchBase data using DAPS
#Create connection with SQL
con =  get_engine(conf_path)

#Get places data
places_df = get_daps_data('geographic_data',con)

#Reverse geocoding
#We focus on the last 2 periods as those are the ones for which we have data

#TODO: turn the below into a function and put it into the reverse_geocoder.py script 
nuts_targets = [2010,2013,2016]

cb_places_nuts_list = [reverse_geocode(place_df=places_df,
                        shape_name=f'nuts2_{str(y)}',
                        shape_file=f'NUTS_RG_01M_{str(y)}_4326_LEVL_2.shp.zip',
                        place_id='id',
                        coord_names= ['longitude','latitude'])['NUTS_ID'] for y in nuts_targets]

#Create a df and turn into a map
cb_places_nuts = pd.concat(cb_places_nuts_list,axis=1)
cb_places_nuts.columns = [f"nuts2_{str(y)}" for y in nuts_targets]
cb_places_dict = cb_places_nuts.to_dict(orient='index')

#Save
with open(f'{project_dir}/data/interim/cb_geos.json','w') as outfile:
    json.dump(cb_places_dict,outfile)
