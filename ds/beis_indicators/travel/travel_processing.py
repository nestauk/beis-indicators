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
    'road_junctions' : 'http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/Road-junctions-travel-times.zip',
    'rail' : 'http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/Rail-stations-travel-times.zip',
    'airports' : 'http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/Airports-travel-times.zip',
    '2013_data' : 'http://data.dft.gov.uk.s3.amazonaws.com/connectivity-data/2013-travel-times.zip'
    }

LSOA_SHAPEFILES = {
    2001: 'https://opendata.arcgis.com/datasets/180a5c44cfc643c0848813f0a81c1bd1_0.zip?outSR=%7B%22latestWkid%22%3A27700%2C%22wkid%22%3A27700%7D',
    2011: 'https://opendata.arcgis.com/datasets/f213065139e3441195803b4155e71e00_0.zip?outSR=%7B%22latestWkid%22%3A27700%2C%22wkid%22%3A27700%7D'
}

MYDIR = (f'{project_dir}/data/raw/travel')
CHECK_FOLDER = os.path.isdir(MYDIR)

def get_travel_data(destination, extract=True, delete_raw=False):
    '''get_cordis_projects
    Download raw OFCOM Broadband data in XML format for a given Framework Programme.
    Args:
        destination (str): Destionation type - road_junctions, rail, airport
        extract (bool): If True then extract projects from zipped XML to csv
        delete_raw (bool): If True then delete original zipped XML
    '''
    if not CHECK_FOLDER:
        os.makedirs(MYDIR,exist_ok=True)
        print("created folder : ", MYDIR)

    logger.info(f'Downloading Travel data for {destination}')

    url = TRAVEL_YEARS_URL[destination]
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

    df_2011 = [gpd.read_file(project_zip.open(text_file.filename))
               for text_file in project_zip.infolist()
               if 'AM' in text_file.filename
                and 'HW' in text_file.filename]

    df_2013 = [gpd.read_file(project_zip.open(text_file.filename))
               for text_file in project_zip_13.infolist()
               if 'AM' in text_file.filename
                and 'HW' in text_file.filename]

    if destination == 'road_junction':
        df_2011 = df_2011[df_2011['NearOrder'] <= 4].reset_index(inplace=True, drop=True)
        df_2013 = df_2013[df_2013['NearOrder'] <= 4].reset_index(inplace=True, drop=True)

    else:
        df_2011 = df_2011[df_2011['NearOrder'] == 0].reset_index(inplace=True, drop=True)
        df_2013 = df_2013[df_2013['NearOrder'] == 0].reset_index(inplace=True, drop=True)

def retrieve_shape_files():

    for year,shp in LSOA_SHAPEFILES.items():
        geo_url = shp
        fname = f'lsoa_latlon_{year}'
        travel_dir = f'{project_dir}/data/raw/travel'

        fout = f'{travel_dir}/{fname}.zip'
        if not os.path.isfile(fout):
            urlretrieve(url, fout)

    shp_file_01 = f'{project_dir}/data/raw/travel/lsoa_latlon_{year}.zip'
    shp_file_11 = f'{project_dir}/data/raw/travel/lsoa_latlon_{year}.zip'
    # project_zip_dir = BROADBAND_YEARS_URL[year]
    project_zip = ZipFile(shp_file_01)
    project_zip_13 = ZipFile(shp_file_11)

    lsoa_shp_geo_re_01 = [geo.read_file(shp_file_01.open(text_file.filename))
                           for text_file in project_zip.infolist()
                           if text_file.filename.endswith('.shp')]

    lsoa_shp_geo_re_11 = [geo.read_file(shp_file_11.open(text_file.filename))
                           for text_file in project_zip.infolist()
                           if text_file.filename.endswith('.shp')]

def lsoa_to_latlon(data, year):

    if year == 2011:
        data = data.merge(lsoa_shp_geo_re_01, on='LSOA_code', how='left')
        data = data[['LSOA_code', 'RepTime', 'Percentage Services', 'uid', 'NearOrder', 'lon', 'lat']]
    if year == 2013:
        data = data.merge(lsoa_shp_geo_re_11, on='LSOA_code', how='left')
        data = data[['LSOA_code', 'RepTime', 'Percentage Services', 'UID', 'NearOrder', 'lon', 'lat']]
        data.rename(columns={'UID':'uid'}, inplace=True)
