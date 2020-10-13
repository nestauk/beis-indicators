import geopandas as gpd
import glob
import json
import logging
import numpy as np
import os
import pandas as pd
from urllib.request import urlretrieve
from zipfile import ZipFile

from beis_indicators import project_dir
from beis_indicators.utils.dir_file_management import save_indicator
from beis_indicators.utils import chunks, camel_to_snake
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator

logger = logging.getLogger(__name__)

TRAVEL_DIR = f'{project_dir}/data/raw/travel'
TRAVEL_YEARS_URL = {
    'road_junctions' : {'url': 'Http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/Road-junctions-travel-times.zip', 'string': 'Junctions'},
    'rail_stations' : {'url': 'http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/Rail-stations-travel-times.zip', 'string': 'Stations'},
    'airports' : {'url': 'http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/Airports-travel-times.zip', 'string': 'Airports'},
    '2013_data' : 'http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/2013-travel-times.zip'
    }

LSOA_SHAPEFILES = {
    2001: 'https://opendata.arcgis.com/datasets/180a5c44cfc643c0848813f0a81c1bd1_0.zip?outSR=%7B%22latestWkid%22%3A27700%2C%22wkid%22%3A27700%7D',
    2011: 'https://opendata.arcgis.com/datasets/f213065139e3441195803b4155e71e00_0.zip?outSR=%7B%22latestWkid%22%3A27700%2C%22wkid%22%3A27700%7D'
}

MYDIR = (f'{project_dir}/data/raw/travel')
CHECK_FOLDER = os.path.isdir(MYDIR)

SHPFILE = (f'{project_dir}/data/raw/travel/lsoa_latlon_2011')
CHECK_FOLDER_SHP = os.path.isdir(SHPFILE)
counter = 0

def get_travel_data(destination, extract=True, delete_raw=False):
    '''get_cordis_projects
    Download raw OFCOM Broadband data in XML format for a given Framework Programme.
    Args:
        destination (str): Destionation type - road_junctions, rail_stations, airport
        extract (bool): If True then extract projects from zipped XML to csv
        delete_raw (bool): If True then delete original zipped XML
    '''


    if not CHECK_FOLDER:
        os.makedirs(MYDIR,exist_ok=True)
        print("created folder : ", MYDIR)

    logger.info(f'Downloading Travel data for {destination}')

    url = TRAVEL_YEARS_URL[destination]['url']
    url_13 = TRAVEL_YEARS_URL['2013_data']
    fname = f'travel_{destination}'
    fname_13 = f'travel_{destination}_13'
    travel_dir = f'{project_dir}/data/raw/travel'
    if not os.path.isdir(travel_dir):
        os.mkdir(travel_dir)
    fout = f'{travel_dir}/{fname}.zip'
    fout_13 = f'{travel_dir}/{fname_13}.zip'
    if not os.path.isfile(fout):
        urlretrieve(url, fout)
    if not os.path.isfile(fout_13):
        urlretrieve(url, fout_13)

    if extract:
        # @run_once
        if not CHECK_FOLDER_SHP:
            retrieve_shape_files()

        _compile_data(destination, delete_raw=delete_raw)


def _compile_data(destination, delete_raw=True):
    """_extract_projects
    Extracts  from zip file downloaded from ONS.
    """

    project_zip_dir = f'{project_dir}/data/raw/travel/travel_{destination}.zip'
    project_zip_dir_13 = f'{project_dir}/data/raw/travel/travel_{destination}_13.zip'
    # project_zip_dir = BROADBAND_YEARS_URL[year]
    project_zip = ZipFile(project_zip_dir)
    project_zip_13 = ZipFile(project_zip_dir_13)

    df_2011 = [pd.read_csv(project_zip.open(text_file.filename))
               for text_file in project_zip.infolist()
               if 'AM' in text_file.filename
                and 'HW' in text_file.filename][0]

    df_2013 = [pd.read_csv(project_zip.open(text_file.filename))
               for text_file in project_zip_13.infolist()
               if 'AM' in text_file.filename
                and 'HW' in text_file.filename
                and TRAVEL_YEARS_URL[destination]['string'] in text_file.filename][0]
    # print(df_2013.columns)
    df_2013 = df_2013.rename(columns={'UID':'uid'})

    if destination == 'road_junctions':
        df_2011 = df_2011[df_2011['NearOrder'] <= 4].reset_index(drop=True)
        df_2013 = df_2013[df_2013['NearOrder'] <= 4].reset_index(drop=True)

    else:
        df_2011 = df_2011[df_2011['NearOrder'] == 0].reset_index(drop=True)
        df_2013 = df_2013[df_2013['NearOrder'] == 0].reset_index(drop=True)
    print(df_2013.head())

    df_2011 = lsoa_to_latlon(df_2011, 2011)
    df_2013 = lsoa_to_latlon(df_2013, 2013)

    df_2011['year'] = 2011
    df_2013['year'] = 2013

    df_final = pd.concat([df_2011, df_2013]).reset_index(drop=True)

    df_final.to_csv(f'{project_dir}/data/interim/{destination}_df.csv')

def retrieve_shape_files():

    for year,shp in LSOA_SHAPEFILES.items():
        geo_url = shp
        fname = f'lsoa_latlon_{year}'
        travel_dir = f'{project_dir}/data/raw/travel'

        fout = f'{travel_dir}/{fname}.zip'
        if not os.path.isfile(fout):
            urlretrieve(geo_url, fout)

        shp_file = f'{project_dir}/data/raw/travel/lsoa_latlon_{year}.zip'

        with ZipFile(shp_file, 'r') as zip_ref:
            zip_ref.extractall(f'{project_dir}/data/raw/travel/lsoa_latlon_{year}')

def read_shp_files():

    lsoa_shp_01 = gpd.read_file(f'{project_dir}/data/raw/travel/lsoa_latlon_2001/Lower_Layer_Super_Output_Areas__December_2001__EW_BGC.shp')
    lsoa_shp_11 = gpd.read_file(f'{project_dir}/data/raw/travel/lsoa_latlon_2011/Lower_Layer_Super_Output_Areas__December_2011__Boundaries_EW_BSC_v2.shp')

    lsoa_shp_geo_01 = lsoa_shp_01.to_crs(epsg=4326)
    lsoa_shp_geo_11 = lsoa_shp_11.to_crs(epsg=4326)


    lsoa_shp_geo_01['lon'] = lsoa_shp_geo_01.geometry.apply(lambda i: i.centroid.x)
    lsoa_shp_geo_01['lat'] = lsoa_shp_geo_01.geometry.apply(lambda i: i.centroid.y)

    lsoa_shp_geo_11['lon'] = lsoa_shp_geo_11.geometry.apply(lambda i: i.centroid.x)
    lsoa_shp_geo_11['lat'] = lsoa_shp_geo_11.geometry.apply(lambda i: i.centroid.y)

    lsoa_shp_geo_re_01 = lsoa_shp_geo_01.rename(columns={'LSOA01CD':'LSOA_code'})
    lsoa_shp_geo_re_11 = lsoa_shp_geo_11.rename(columns={'LSOA11CD':'LSOA_code'})

    geo_dict = {2001: lsoa_shp_geo_re_01, 2011: lsoa_shp_geo_re_11}

    return geo_dict



def lsoa_to_latlon(data, year):
    if year == 2011:
        lsoa_shp_geo_re_01 = read_shp_files()[2001]
        data = data.merge(lsoa_shp_geo_re_01, on='LSOA_code', how='left')
        data = data[['LSOA_code', 'RepTime', 'Percentage Services', 'uid', 'NearOrder', 'lon', 'lat']]

    elif year == 2013:
        lsoa_shp_geo_re_11 = read_shp_files()[2011]
        data = data.merge(lsoa_shp_geo_re_11, on='LSOA_code', how='left')
        data = data[['LSOA_code', 'RepTime', 'Percentage Services', 'uid', 'NearOrder', 'lon', 'lat']]

    return data

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper
