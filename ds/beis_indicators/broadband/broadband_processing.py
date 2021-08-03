# +

import geopandas as gpd
import glob
import json
import logging
import numpy as np
import os
import pandas as pd
import requests
import re
from datetime import datetime
from urllib.request import urlretrieve
from zipfile import ZipFile
from bs4 import BeautifulSoup
from functools import lru_cache
# -

from beis_indicators import project_dir
from beis_indicators.utils.dir_file_management import save_indicator
from beis_indicators.utils import chunks, camel_to_snake
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator

logger = logging.getLogger(__name__)

BROADBAND_BASE = "https://www.ofcom.org.uk/research-and-data/multi-sector-research/infrastructure-research{}"
BROADBAND_DIR = f'{project_dir}/data/raw/broadband'
MYDIR = (f'{project_dir}/data/raw/broadband')
CHECK_FOLDER = os.path.isdir(MYDIR)


# +
last_year = datetime.now().year - 1
pre_years  = range(2015, 2016+1)
current_years = range(2017, last_year+1)
BROADBAND_YEARS_URL = {year:BROADBAND_BASE.format('/connected-nations-{}/downloads'.format(year)) for year in pre_years}
BROADBAND_YEARS_URL_POST = {year:BROADBAND_BASE.format('/connected-nations-{}/data-downloads'.format(year)) for year in current_years}

BROADBAND_YEARS_URL.update(BROADBAND_YEARS_URL_POST)


# -

def get_file_link_pre_2018(link):
    """Finds string directing to dataset"""
    pre_link_element = {"headers": "table70995r1c2"}
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    for tag in soup.find_all("td", pre_link_element):
        tag_ = tag.find('a', text= re.compile("Postcode | postcode"))
        link = tag_["href"]
        
        if not link.endswith("zip"):
            continue
        else: 
            return link
#         return ONS_BASE.format(link)


def get_file_link_post_2018(link):
    """Finds string directing to dataset"""
    post_link_element = {"headers": "table15976r1c2 table15976r2c1"}
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    for tag in soup.find_all("td", post_link_element):        
        if len(tag) ==1:
            tag_ = tag.find('a', href=True)
            link = tag_["href"]
            if not link.endswith("zip"):
                continue
            else:
                return link
            
        elif len(tag) == 0:
            continue
            
        else:
            tag_ = tag.find('a', text= re.compile(r"Coverage and performance ZIP| Postcode | performance postcode"))
            link = tag_["href"]
            if not link.endswith("zip"):
                continue
            else:
                return link


@lru_cache()
def create_data_links():
    BROADBAND_DATA_URL = {
        2014: 'http://www.ofcom.org.uk/static/research/ir/Fixed_postcode.zip'
    }
    for k,v in BROADBAND_YEARS_URL.items():
        if k <= 2017:

            BROADBAND_DATA_URL[k] = get_file_link_pre_2018(v)

        elif k > 2017:
            BROADBAND_DATA_URL[k] = get_file_link_post_2018(v)
            
    return BROADBAND_DATA_URL


def get_broadband_data(year, extract=True, delete_raw=False):
    '''get_cordis_projects
    Download raw OFCOM Broadband data in XML format for a given Framework Programme.
    Args:
        year (str): Year of observation of dataset - ranges from 2014 to 2019
        extract (bool): If True then extract projects from zipped XML to csv
        delete_raw (bool): If True then delete original zipped XML
    '''
    if not CHECK_FOLDER:
        os.makedirs(MYDIR,exist_ok=True)
        print("created folder : ", MYDIR)

    logger.info(f'Downloading Broadband data for {year}')

    url = create_data_links()[year]
    fname = f'broadband_{year}'
    if not os.path.isdir(BROADBAND_DIR):
        os.mkdir(BROADBAND_DIR)
    fout = f'{BROADBAND_DIR}/{fname}.zip'
    if not os.path.isfile(fout):
        urlretrieve(url, fout)

    if extract:
        print('compiling')
        _compile_data(year, delete_raw=delete_raw)

def _compile_data(year, delete_raw=True):
    """_extract_projects
    Extracts  from zip file downloaded from OFCOM.
    """

    logger.info(f'Parsing Broadband OFCOM {year}. This might take a while.')
    project_zip_dir = f'{project_dir}/data/raw/broadband/broadband_{year}.zip'
    # project_zip_dir = BROADBAND_YEARS_URL[year]
    project_zip = ZipFile(project_zip_dir)
    postcode_latlon = pd.read_csv(f'{project_dir}/data/aux/final_postcode_lat_lon.csv')

    if (year == 2016) or (year == 2017):

        dfs = [pd.read_csv(project_zip.open(text_file.filename))
               for text_file in project_zip.infolist()
               if text_file.filename.endswith('.csv')]
        df = pd.concat(dfs,ignore_index=True)
        df = format_speeds(df, year)
        df = postcode_to_latlon(df, postcode_latlon, year)
        df['year'] = [year] * len(df)
        df.to_csv(f'{project_dir}/data/raw/broadband/broadband_{year}.csv', index=False)

    elif year >= 2019:

        dfs = [pd.read_csv(project_zip.open(text_file.filename))
                for text_file in project_zip.infolist()
                 if not text_file.filename.endswith('/')
                 if 'pc_performance' in text_file.filename]
        df = pd.concat(dfs,ignore_index=True)
        df = format_speeds(df, year)
        df = postcode_to_latlon(df, postcode_latlon, year)
        df['year'] = [year] * len(df)
        df.to_csv(f'{project_dir}/data/raw/broadband/broadband_{year}.csv', index=False)
    else:

        dfs = [pd.read_csv(project_zip.open(project_zip.infolist()[0]))]
        df = pd.concat(dfs,ignore_index=True)
        df = format_speeds(df, year)
        df = postcode_to_latlon(df, postcode_latlon, year)
        df['year'] = [year] * len(df)
        df.to_csv(f'{project_dir}/data/raw/broadband/broadband_{year}.csv', index=False)

    if delete_raw:
        os.remove(project_zip_dir)

def postcode_to_latlon(data, postcode_data, year):

    if (year == 2014) or (year == 2015):
        # removal of invalid potcodes found in 2014 dataset
        # logger.info(data.head())
        x = data['postcode'].values
        y = postcode_data['postcode'].values

        diff = list(set(x).difference(set(y)))

        data = data[~data['postcode'].isin(diff)].reset_index(drop=True)

        data = pd.merge(data, postcode_data, on="postcode")
        data = data[['postcode','Average download speed (Mbit/s) by PC', 'latitude', 'longitude']]
        data.columns = ['postcode', 'speed', 'latitude', 'longitude']

    else:
        data = pd.merge(data, postcode_data, on="postcode")
        data = data[['postcode','Average download speed (Mbit/s)', 'latitude', 'longitude']]
        data.columns = ['postcode', 'speed', 'latitude', 'longitude']

    data.drop(['postcode'], axis=1, inplace=True)
    return data

def format_speeds(data, year):

    if (year == 2014) or (year == 2015):

        data.loc[data['Average download speed (Mbit/s) by PC'] == '<4', 'Average download speed (Mbit/s) by PC'] = 4
        data['Average download speed (Mbit/s) by PC'] = data['Average download speed (Mbit/s) by PC'].apply(lambda x: float(x) if type(x) == str else x)

    else:

        data['Average download speed (Mbit/s)'] = data['Average download speed (Mbit/s)'].apply(lambda x: float(x))

    return data


def main_run():
    years = list(pre_years)+list(current_years)
    for year in years:
        get_broadband_data(year)


if __name__ == "__main__":
#
    main_run()
