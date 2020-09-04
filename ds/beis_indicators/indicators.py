import os
import re
import requests
import geopandas as gpd
import pandas as pd
import numpy as np
from urllib.request import urlretrieve
from zipfile import ZipFile
import logging


from beis_indicators.utils.geo_utils import generate_year_spec
from beis_indicators import project_dir


def _setattr(obj, value, value_name, regex, url):
    allowed_values = _get_available(regex, url)
    if value not in allowed_values:
        raise ValueError(f"'{value_name}' must be one of {allowed_values}")
    setattr(obj, value_name, value)


def _get_available(regex, url):
    r = requests.get(url)
    values = set(int(yr) for yr in
                 re.findall(regex, r.text))
    return values

class Coder:
    def __init__(self):
        pass

    def _load_shapes(self):
        pass

    def code_points(self):
        pass

    def _reverse_geocode(self, points, year):
        """_reverse_geocode
        """
        shape = self.shapes[year].to_crs(self.PROJECTION)
        joined = gpd.sjoin(points, shape, op='within', how='right')
        return joined

    def _coordinates_to_points(self, x, y, data=None):
        """_coordinates_to_points
        """
        return gpd.GeoDataFrame(data=data,
                geometry=gpd.points_from_xy(x, y))


class NutsCoder(Coder):
    YEAR_REGEX = 'NUTS ([0-9]+)'
    RES_REGEX = '1:([0-9]+) Million'
    TOP_URL = ("https://gisco-services.ec.europa.eu/"
               "distribution/v2/nuts/download")
    SHAPE_URL = (f"{TOP_URL}/"
               "ref-nuts-{year}-{resolution}m.geojson.zip")
    NESTED_FILE = 'NUTS_RG_{resolution}M_{year}_4326_LEVL_{level}.geojson'
    PROJECTION = 'EPSG:4326'
    GEOGRAPHY = 'nuts'
    SHAPE_DIR = (f'{project_dir}/data/raw/shapefiles/')

    def _get_shape(self, year):
        """_get_shape
        """
        resolution = str(self.resolution).zfill(2)
        url = self.SHAPE_URL.format(year=year, resolution=resolution)
        fname = url.split('/')[-1]
        fout = f'{self.SHAPE_DIR}/{fname}'
        urlretrieve(url, fout)

    def __init__(self, resolution=1, level=2, nuts_countries=['UK']):
        _setattr(self, resolution, 'resolution', self.RES_REGEX, self.TOP_URL)
        self.nuts_countries = nuts_countries
        self.level = level
        self._load_shapes()

    def _load_shapes(self):
        self.shapes = {}
        years_available = _get_available(self.YEAR_REGEX, self.TOP_URL)
        resolution = str(self.resolution).zfill(2)
        for year in years_available:
            shape_zip_dir = os.path.join(self.SHAPE_DIR, 
                                    f'ref-nuts-{year}-{resolution}m.geojson.zip')
            exists = os.path.isfile(shape_zip_dir)
            if not exists:
                self._get_shape(year)
            gdf = gpd.read_file(zipfile.open(nested))
            if self.nuts_countries is not None:
                gdf = (gdf.set_index('CNTR_CODE')
                          .loc[self.nuts_countries]
                          .reset_index())
            self.shapes[year] = gdf

    def code_points(self, x, y, year, projection, data=None):
        """code_points
        """
        shape = self.shapes[year]
        if projection != self.PROJECTION:
            # reverse x and y because eurostat uses lat, lon for polygons
            # rather than lon, lat
            y, x = translate_coordinates(np.array(x), np.array(y),
                    projection, self.PROJECTION)
        points = self._coordinates_to_points(x, y, data=data)
        joined = self._reverse_geocode(points, year)
        joined = joined.rename(columns={'NUTS_ID': 'nuts_id'})
        return joined

class LepCoder(Coder):
    TOP_URL = "https://opendata.arcgis.com/datasets/"
    YEAR_URLS = {
            2014: "17c92615a55f4dbf945e8eaf642eaa87_0.geojson",
            2017: "ca2ff82048594beca3b67688814e8fe4_0.geojson",
            2020: "0af0f6e04abf44f48868b441afd67e0e_0.geojson",
            }
    FILE = 'lep_{year}.geojson'
    PROJECTION = 'EPSG:27700'
    GEOGRAPHY = 'lep'
    SHAPE_DIR = (f'{project_dir}/data/raw/shapefiles/')

    def __init__(self):
        self._load_shapes()

    def _get_shape(self, year, url):
        """_get_shape
        """
        fname = self.FILE.format(year=year)
        fout = f'{self.SHAPE_DIR}/{fname}'
        urlretrieve(url, fout)

    def _load_shapes(self):
        self.shapes = {}
        for year, file_url in self.YEAR_URLS.items():
            fname = self.FILE.format(year=year)
            shape_dir = os.path.join(self.SHAPE_DIR, fname)
            exists = os.path.isfile(shape_dir)
            if not exists:
                self._get_shape(year, f"{self.TOP_URL}{file_url}")
            gdf = gpd.read_file(shape_dir)
            self.shapes[year] = gdf

    def code_points(self, x, y, year, projection, data=None):
        """code_points
        """
        shape = self.shapes[year]
        if projection != self.PROJECTION:
            x, y = translate_coordinates(np.array(x), np.array(y),
                    projection, self.PROJECTION)
        points = self._coordinates_to_points(x, y, data=data)
        joined = self._reverse_geocode(points, year)
        joined = joined.rename(columns={f'lep{year}cd': 'lep_id'})
        return joined

def points_to_indicator(data, value_col, coder, 
        aggfunc=np.mean, value_rename=None, projection=None, 
        x_col='lon', y_col='lat', dp=2):
    """points_to_indicator

    Args
        data (pd.DataFrame): Dataframe containing discrete point data to create
            an indicator. Must have columns:
                - the year each value was created
                - the values themselves
                - x coordinates
                - y coordinates
        value_col (str): Name of the column that has the values from which to
            created the indicator.
        boundaries (dict): A dictionary where values are `geopandas` dataframes
            containing boundary geometries and keys are the year that the 
            specific boundary set was introduced or enforced.
        geography (str): Selects the geography type. Must be nuts or lep.
        aggfunc (function): Function used to aggregate points within a boundary.
            Default is `np.mean`.
        value_rename (str): Optional. If provided, then the value column will be
            renamed as this for the output indicator.
        projection (str): Geographic projection of the data.
        x_col (str): Column of the x coordinate.
        y_col (str): Column of the y coordinate.
        dp (int): Decimal places to round the final indicator values to. If 
            None, rounding will not be applied.

    Returns:
        indicator (pd.DataFrame): Final indicator dataframe with columns:
            - year: year of the indicator value
            - <geography>_id: region code
            - <geography>_year_spec: specification year of the boundaries
            - <value_col> or <rename_value>: the indicator values
    """
    geo_type = coder.GEOGRAPHY
    year_spec_col = f'{geo_type}_year_spec'
    id_col = f'{geo_type}_id'
    data[year_spec_col] = generate_year_spec(data, geo_type)
    
    aggregated = []
    for year, group in data.groupby('year'):
        year_spec = np.abs(group[year_spec_col].max())
        joined = coder.code_points(
                group[x_col], group[y_col], year_spec, projection, group)
        agg_cols = [id_col, 'year', year_spec_col]
        agg = (joined
                .groupby(agg_cols, as_index=False)[value_col]
                .apply(aggfunc)
                .reset_index())
        aggregated.append(agg)
    indicator = pd.concat(aggregated)
    
    if value_rename is not None:
        indicator = indicator.rename(columns={0: value_rename})
        value_col = value_rename
    else:
        indicator = indicator.rename(columns={0:value_col})

    indicator = indicator[['year', id_col, year_spec_col, value_col]]
    indicator['year'] = indicator['year'].astype(int)
    indicator[year_spec_col] = indicator[year_spec_col].astype(int)
    if dp is not None:
        indicator[value_col] = np.round(indicator[value_col], dp)
    
    return indicator

