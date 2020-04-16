import os
import json
import requests
from zipfile import ZipFile
from io import BytesIO
import re
import pandas as pd
import numpy as np
import logging

import beis_indicators
from beis_indicators.geo.reverse_geocoder import *
from beis_indicators.utils.dir_file_management import *

# Create logger
logger = logging.getLogger(__name__)

# Define project base directory
project_dir = beis_indicators.project_dir

# URLS and Paths
URL = "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/680986/opendatadomestic.zip"
DATA_RAW = f'{project_dir}/data/raw/'
TRADE_RAW = f"{project_dir}/data/raw/trademarks/"

# Load the shapefile lookup
with open(f'{project_dir}/data/aux/shapefile_urls.json', 'r') as infile:
    shape_lookup = json.load(infile)

# Get all the shapefiles
for name in shape_lookup.keys():
    get_shape(name, path=f"{DATA_RAW}/shapefiles")

# Functions
def _tidy_columns(columns):
    
    return [re.sub(" ", "_", x).lower() for x in columns]

def get_trademarks(url):
    """
    Function to collect the trademark data
    Args:
        url (str) is the link for the data
    """
    if  os.path.exists(f"{TRADE_RAW}/OpenDataDomestic.txt"):
        logger.info("Already collected the data")

    else:
        req = requests.get(url)

        # Extracts the text file (in raw)
        logger.info("Saving the raw data")

        ZipFile(BytesIO(req.content)).extract(
            "OpenDataDomestic.txt", path=f"{TRADE_RAW}/"
        )

    if os.path.exists(f"{TRADE_RAW}/trademarks_processed_df.csv"):

        logger.info("Already processed the data")
        text_df = pd.read_csv(f"{TRADE_RAW}/trademarks_processed_df.csv")

    else:
        logger.info("Creating dataframe")

        # Reads the text file
        with open(
            f"{TRADE_RAW}/OpenDataDomestic.txt",
            "r",
            encoding="utf-16",
        ) as infile:

            # There are a few corrupted lines with errors (more than 62 fields)
            text = infile.read().split("\n")

            text_clean = [x.split("|") for x in text if len(x.split("|")) == 62]

            bad_lines = len(text) - len(text_clean)
            bad_lines_rate = np.round(bad_lines / len(text), 3)

            logger.info(
                f"We found {bad_lines} bad lines, {100*bad_lines_rate}% of the total"
            )

        # Creates the dataframe (note that the first row are the headers)
        text_df = pd.DataFrame(text_clean[1:], columns=text_clean[0])

        # Tidy the columns
        text_df.columns = _tidy_columns(text_df.columns)

        text_df.to_csv(f"{TRADE_RAW}/trademarks_processed_df.csv",
                       index=False)

    return text_df

def geocode_trademarks(df, geo_code=['long','lat']):
    """
    This function reverse geocodes a trademark df using the postcode of the applicant.
    It returns the lat and lon for each trademark

    Args:
        df (df) is a dataframe with organisation postcodes
        geo_code (str) is the geocode in the NSPL database that we want to use
    """
    df_c = df.copy()
    # We have trailing spaces in the postcodes
    
    df_c["postcode"] = [
        x.strip() if pd.isnull(x) is False else np.nan for x in df_c['postcode']]

    # Read nspl
    nspl = pd.read_csv(f"{DATA_RAW}/nspl/Data/NSPL_FEB_2020_UK.csv") 

    # The trademark dataset only provides information for the first part of the postcode
    # We split the nspl postcodes to merge on a smaller dataset
    nspl["pcds_1st"] = nspl["pcds"].apply(lambda x: x.split(" ")[0])

    nspl_short = nspl.drop_duplicates("pcds_1st")[["pcds_1st"]+geo_code]

    merged = pd.merge(df_c, nspl_short, left_on="postcode", right_on="pcds_1st")

    return merged

def make_reverse_geocode_lookup(df,nuts_years=[2010,2013,2016],coords=['long','lat']):
    '''
    Function to create a map between geography and various nuts taxonomies

    Args:
        df (df) is the df with lat,lons that we want to reverse geocode
        nuts_years (list) are the nuts years that we want to consider
        coords (str) are the coordinate variable names

    '''
    container = []

    for y in nuts_years:

        rev = reverse_geocode(place_df=df,
                              shape_name=f'nuts2_{str(y)}',
                              shape_file=f'NUTS_RG_01M_{str(y)}_4326_LEVL_2.shp.zip',
                              place_id = 'pcds_1st',
                              coord_names=coords)['NUTS_ID']
        container.append(rev)

    all_nuts = pd.concat(container,axis=1)

    all_nuts.columns = [f'nuts2_{str(y)}' for y in nuts_years]

    all_nuts_map = all_nuts.to_dict(orient='index')

    return(all_nuts_map)

def reverse_geocode_trademarks(df,tm_year = 'published',
                               tm_threshold=2010,method='time_consistent'):
    '''
    This function takes the df with lats and lons and labels with NUTS based 
    on their publication year

    Args:
        df (df) is a dataframe with longitudes and latitudes
        tm_year (str) is the date variable we use to geocode
        tm_threshold (int) is the minimum year
        method (str) is whether we are creating the indicator using a time 
        consistent approach 
            (each year in its NUTS category) or using the latest nuts
    '''
    df_2 = df.copy()

    #Drop missing years
    df_2.dropna(axis=0,subset=[tm_year],inplace=True)

    #Create year
    df_2['year'] = [int(x.split('-')[0]) for x in df_2[tm_year]]

    #Focus on years after the threshold
    df_2 = df_2.loc[df_2['year']>=tm_threshold]

    #Create unique postcodee df for reverse geocoding. Here we want to 
    #remove duplicates to speed things up
    
    pc_lookup = df_2.drop_duplicates('pcds_1st')[['pcds_1st','long','lat']]

    #We create a reverse geocoding lookup
    pc_nuts_map = make_reverse_geocode_lookup(pc_lookup,nuts_years=[2010,2013,2016])

    if method == 'time_consistent':
        df_2['nuts_code'] = [pc_nuts_map[row['pcds_1st']][get_nuts_category(
                                row['year'])] 
            if row['pcds_1st'] in pc_nuts_map.keys() else np.nan for rid,row in df_2.iterrows()]
    else:
        df_2['nuts_code'] = [pc_nuts_map[row['pcds_1st']]['nuts2_2016'] if 
            row['pcds_1st'] in pc_nuts_map.keys() else np.nan for rid,row in df_2.iterrows()]

    return(df_2)


def subset_trademark_category(tdf,selected_classes):
    '''
    Takes the trademark df and subsets it to focus on a few classes

    Args:
        tdf (df) is the trademarks df
        selected_classes (list) are the classes we are interested in

    '''
    sel_df = tdf.loc[tdf[selected_classes].sum(axis=1)>0]
    return(sel_df)

def make_trademarks(URL,detailed_classes):
    """
    Function to make the trademark dataset. It collects the data and geocodes it.

    Args:
        URL (str) is the link where we collect the trademark data
        detailed_classes (dict) is a dict where the keys are names of 
        #detailed classes and the values lists of class codes
    """
    # Download and process the trademark data
    logger.info("Downloading the data")
    tm_df = get_trademarks(URL)

    logger.info("Geocoding the data")
    tm_df_geo = geocode_trademarks(tm_df)

    logger.info("Reverse geocoding the data")
    tm_df_nuts = reverse_geocode_trademarks(tm_df_geo)

    for x in tm_df_nuts.columns:
        if "class" in x:
            tm_df_nuts[x] = pd.to_numeric(tm_df_nuts[x])

    #Create trademarks
    logger.info("Creating indicators")
    all_trademarks = tm_df_nuts.groupby(['nuts_code','year']).size()
    all_trademarks.name = 'total_trademarks'

    tm = make_indicator(all_trademarks,
                   {'total_trademarks':'total_trademarks'},
                   'year')

    save_indicator(tm,f"{project_dir}/data/processed/trademarks",'total_trademarks')

    #Create specialised trademarks
    for k,v in detailed_classes.items():
        sel = subset_trademark_category(tm_df_nuts,v)
        sel_grouped = sel.groupby(['nuts_code','year']).size()
        sel_grouped.name = k
        stm = make_indicator(sel_grouped,
                             {k:f"total_trademarks_{k}"},
                             "year")
        save_indicator(stm,f"{project_dir}/data/processed/trademarks",
                       f"total_trademarks_{k}")

if __name__ == "__main__":
    make_trademarks(URL,{'scientific':['class42']})
