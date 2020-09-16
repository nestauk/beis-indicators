
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

BROADBAND_DIR = f'{project_dir}/data/raw/broadband'
BROADBAND_YEARS_URL = {
    2014: 'http://www.ofcom.org.uk/static/research/ir/Fixed_postcode.zip',
    2015: 'http://www.ofcom.org.uk/static/research/connected-nations2015/Fixed_Postcode_2015.zip',
    2016: 'https://www.ofcom.org.uk/static/research/connected-nations2016/2016_fixed_pc_r01.zip',
    2017: 'https://www.ofcom.org.uk/static/research/connected-nations2017/fixed-postcode-2017.zip',
    2018: 'https://www.ofcom.org.uk/__data/assets/file/0011/131042/201809_fixed_pc_r03.zip',
    2019: 'https://www.ofcom.org.uk/__data/assets/file/0036/186678/connected-nations-2019-fixed-postcode-data.zip'
}

postcode_latlon = pd.read_csv(f'{project_dir}/data/raw/final_postcode_lat_lon.csv')

MYDIR = (f'{project_dir}/data/raw/broadband')
CHECK_FOLDER = os.path.isdir(MYDIR)

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

    url = BROADBAND_YEARS_URL[year]
    fname = f'broadband_{year}'
    broadband_dir = f'{project_dir}/data/raw/broadband'
    if not os.path.isdir(broadband_dir):
        os.mkdir(broadband_dir)
    fout = f'{broadband_dir}/{fname}.zip'
    if not os.path.isfile(fout):
        urlretrieve(url, fout)

    if extract:
        _compile_data(year, delete_raw=delete_raw)

def _compile_data(year, delete_raw=True):
    """_extract_projects
    Extracts  from zip file downloaded from OFCOM.
    """

    logger.info(f'Parsing Broadband OFCOM {year}. This might take a while.')
    project_zip_dir = f'{project_dir}/data/raw/broadband/broadband_{year}.zip'
    # project_zip_dir = BROADBAND_YEARS_URL[year]
    project_zip = ZipFile(project_zip_dir)

    if (year == 2016) or (year == 2017):

        dfs = [pd.read_csv(project_zip.open(text_file.filename))
               for text_file in project_zip.infolist()
               if text_file.filename.endswith('.csv')]
        df = pd.concat(dfs,ignore_index=True)
        df = format_speeds(df, year)
        df = postcode_to_latlon(df, postcode_latlon, year)
        df['year'] = [year] * len(df)
        df.to_csv(f'{project_dir}/data/raw/broadband/broadband_{year}.csv', index=False)

    elif year == 2019:

        dfs = [pd.read_csv(project_zip.open(text_file.filename))
                for text_file in project_zip.infolist()
                 if not text_file.filename.endswith('/')
                 if '201905_fixed_pc_performance' in text_file.filename]
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



# if __name__ == "__main__":
# #
#     years = [2014, 2015, 2016, 2017, 2018, 2019]
#
#     for year in years:
#         get_broadband_data(year)
