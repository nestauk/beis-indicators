import geopandas as gpd
import logging
import numpy as np
import os
import pandas as pd
from zipfile import ZipFile

from beis_indicators import project_dir
from beis_indicators.utils.dir_file_management import save_indicator
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator

logger = logging.getLogger(__name__)


def get_pollution_data(year, raw_data_dir, pollution_type):
    '''get_pollution_data
    Downloads and stores pollution data from https://uk-air.defra.gov.uk/data/pcm-data
    
    Args:
        year (int): Year to collect data from. Check website for coverage.
        raw_data_dir (str): Directory where raw pollution data is stored.
        pollution_type (str): Name of pollutant. Choices are currently pm10 
            and pm25, no2 or nox.
    '''
    logger.info(f'Fetching {pollution_type} data from DEFRA')

    base_url = 'https://uk-air.defra.gov.uk/datastore/pcm/map{}.csv'
        
    if not os.path.isdir(raw_data_dir):
        os.mkdir(raw_data_dir)
    
    if pollution_type in ['pm10', 'pm25']:
        fname = f'{pollution_type}{year}g'
    else:
        fname = f'{pollution_type}{year}'

    df = pd.read_csv(base_url.format(fname), header=5, na_values='MISSING')
    df.rename(columns={fname: pollution_type}, inplace=True)

    df.to_csv(f'{raw_data_dir}/map{pollution_type}{year}.csv', index=False)


def load_pollution_data(year, raw_data_dir, pollution_type='pm10'):
    '''load_pollution_data
    Loads pollution data. If data is not present, downloads from 
    https://uk-air.defra.gov.uk/data/pcm-data
    
    Args:
        year (int): Year of data to load. Check website for coverage.
        raw_data_dir (str): Directory where raw pollution data is stored.
        pollution_type (str): Name of pollutant. Choices are currently pm10 
            and pm25, no2 or nox.

    Returns:
        (pandas.DataFrame): Modelled pointwise pollution data.
    '''
    fin = f'{raw_data_dir}/map{pollution_type}{year}.csv'
    
    if not os.path.isfile(fin):
        get_pollution_data(year, pollution_type)
        
    return pd.read_csv(fin)


def make_air_pollution_nuts(years, raw_data_dir, shapefile_dir,
        pollution_type='pm10', nuts_level=2, aggfunc=np.mean):
    '''make_air_pollution_nuts
    Creates air pollution indicator for NUTS regions over a range of years, using
    modelled point data from DEFRA at a 1km resolution.
    
    Output is a DataFrame of aggregated values at the level of NUTS regions.
    
    Args:
        years (iter of int): Collects pollution data and creates indicators over
            this range of years.
        raw_data_dir (str): Directory where raw pollution data is stored.
        shapefile_dir (str): Directory where shapefiles are stored.
        pollution_type (str): Name of pollutant. Choices are currently pm10 
            and pm25, no2 or nox. Defaults to pm10.
        nuts_level (int): NUTS region level. Can be 1, 2 or 3.
        aggfunc (function): Function used to aggregate point data within a region, 
            for example finding the average, maximum or percentile value. Default 
            is np.mean.
            
    Returns:
        df (pandas.DataFrame): DataFrame of processed indicator.
    '''
    pin = 'epsg:27700'
    pout = 'epsg:4326'
     
    dfs = []
    for year in years:
        logger.info(f'Creating {year} {pollution_type} indicator for NUTS{nuts_level}')

        pollution = load_pollution_data(year, raw_data_dir, pollution_type)

        pollution['longitude'], pollution['latitude'] = translate_coordinates(
            pollution['x'].values, pollution['y'].values, pin, pout)
        pollution_gdf = coordinates_to_points(pollution, 'latitude', 'longitude')
        
        nuts_spec_year = nuts_earliest(year)
        nuts = load_nuts_regions(nuts_spec_year, shapefile_dir, level=nuts_level)
        nuts = nuts.to_crs(pout.upper())
        
        pollution_gdf = gpd.sjoin(pollution_gdf, nuts, op='within')
        
        aggregated = (pollution_gdf.groupby('NUTS_ID')[pollution_type]
                      .apply(aggfunc)
                      .reset_index())
        aggregated['nuts_year_spec'] = nuts_spec_year
        aggregated['year'] = year
        
        value_header = f'air_pollution_{aggfunc.__name__}_{pollution_type}'
        headers = {
            pollution_type: value_header,
            'NUTS_ID': 'nuts_id'
        }
        aggregated = aggregated.rename(columns=headers)
        dfs.append(aggregated)
    
    df = pd.concat(dfs)
    df = df[['year', 'nuts_id', 'nuts_year_spec', value_header]]
    return df


def make_air_pollution_leps(years, raw_data_dir, shapefile_dir, 
        pollution_type='pm10', aggfunc=np.mean):
    '''make_air_pollution_leps
    Creates air pollution indicator for LEP regions over a range of years, using
    modelled point data from DEFRA at a 1km resolution.
    
    Output is a DataFrame of aggregated values at the level of LEP regions.
    
    Args:
        years (iter of int): Collects pollution data and creates indicators over
            this range of years.
        raw_data_dir (str): Directory where raw pollution data is stored.
        shapefile_dir (str): Directory where shapefiles are stored.
        pollution_type (str): Name of pollutant. Choices are currently pm10 
            and pm25, no2 or nox. Defaults to pm10.
        aggfunc (function): Function used to aggregate point data within a region, 
            for example finding the average, maximum or percentile value. Default 
            is np.mean.
            
    Returns:
        df (pandas.DataFrame): DataFrame of processed indicator.
    '''
    
    proj = 'epsg:27700'
    
    dfs = []
    for year in years:
        logger.info(f'Creating {year} {pollution_type} indicator for LEPs')
        pollution = load_pollution_data(year, raw_data_dir, pollution_type)
        pollution_gdf = coordinates_to_points(pollution, 'x', 'y')
        
        lep_year_spec = leps_year_spec(year)
        leps = load_leps_regions(lep_year_spec, shapefile_dir)
        leps = leps.to_crs(proj.upper())
        
        pollution_gdf = gpd.sjoin(pollution_gdf, leps, op='within')
        
        region_col = f'lep{str(lep_year_spec)[-2:]}cd'
        aggregated = (pollution_gdf.groupby(region_col)[pollution_type]
                      .apply(aggfunc)
                      .reset_index())
        aggregated['lep_year_spec'] = lep_year_spec
        aggregated['year'] = year
        
        value_header = f'air_pollution_{aggfunc.__name__}_{pollution_type}'
        headers = {
            pollution_type: value_header,
            region_col: 'lep_id'
        }
        aggregated = aggregated.rename(columns=headers)
        dfs.append(aggregated)
    
    df = pd.concat(dfs)
    df = df[['year', 'lep_id', 'lep_year_spec', value_header]]
    return df


raw_data_dir = f'{project_dir}/data/raw/defra'
shapefile_dir = f'{project_dir}/data/raw/shapefiles'
years = range(2007, 2019)
aggfunc = np.mean
pollution_type = 'pm10'
out_dir = f'{project_dir}/data/processed/defra'
var_name = f'air_pollution_{aggfunc.__name__}_{pollution_type}'

coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

pollution = []
for year in years:
    p = load_pollution_data(year, raw_data_dir, pollution_type)
    p['year'] = year
    pollution.append(p)
pollution = pd.concat(pollution)

for geo, coder in coders.items():
    mean_pm10 = points_to_indicator(pollution, value_col='pm10', coder=coder,
                    aggfunc=np.mean, value_rename=var_name,
                    projection='EPSG:27700', x_col='x', y_col='y')
    save_indicator(mean_pm10, 'defra', geo)

