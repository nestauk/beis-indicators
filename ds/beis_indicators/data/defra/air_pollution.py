import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj


BASE_URL = 'https://uk-air.defra.gov.uk/datastore/pcm/map{}{}g.csv'

POLLUTION_TYPES = {
        'pm10': 'pm10',
        }

BNG = pyproj.Proj('epsg:27700')
WGS84 = pyproj.Proj('epsg:4326')


def _get_modelled_data(pollution_type, year):
    '''_get_modelled_data
    Retrieves a modelled pollution dataset for a given year and pollution type
    from the DEFRA portal.
    '''
    defra_pollution_code = POLLUTION_TYPES[pollution_type]
    url = BASE_URL.format(defra_pollution_code, year)
    df = pd.read_csv(url, header=5, na_values='MISSING')
    pollution_col = f'{pollution_type}{year}g'
    df = df.rename(columns={pollution_col: 'value'})
    df = df.dropna()
    df['lat'], df['lon'] = pyproj.transform(BNG, WGS84, df['x'].values, df['y'].values)
    df['year'] = year
    df = df[['year', 'lat', 'lon', 'value']]
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lon'], df['lat']))
    return gdf

def _get_nuts2_boundaries():
    '''_get_nuts2_boundaries
    Retrieves NUTS 2 2016 UK boundaries at full resolution. 
    '''
    # TODO change to use Open Geography Portal REST API to select any year
    nuts2_full_resolution_uk_boundaries_url = ('https://opendata.arcgis.com/datasets/'
                                               '48b6b85bb7ea43699ee85f4ecd12fd36_0.geojson')
    df = gpd.read_file(nuts2_full_resolution_uk_boundaries_url)
    return df

def _merge_points_in_polys(points, polys):
    points_in_poly = sjoin(points, polys, op='within')
    return points_in_poly

def get_uk_nuts2_air_pollution(pollution_type, year, nuts_year=2016, 
        aggfunc=np.mean):
    '''get_uk_nuts2_air_pollution
    Creates a dataset of modelled point air pollution data aggregated at NUTS2.
    '''
    points = _get_modelled_data(pollution_type, year)
    polys = _get_nuts2_boundaries()
    data = _merge_points_in_polys(points, polys)
    data = data[['nuts218nm', 'value']]

    agg = data.groupby('nuts218nm').agg(aggfunc).reset_index()

    agg['year'] = year
    agg['nuts_spec_year'] = nuts_year
    value_name = f'air_pollution_{aggfunc.__name__}_{pollution_type}'
    agg = agg.rename(columns={'nuts218nm': 'nuts_id', 'value': value_name})

    agg = agg[['nuts_id', 'nuts_year_spec', value_name, 'year']]

    return agg
