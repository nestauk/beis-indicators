import os
import re
import requests
import geopandas as gpd
import pandas as pd
import numpy as np
import pyproj
from urllib.request import urlretrieve
from zipfile import ZipFile
import logging

from beis_indicators import project_dir


logger = logging.getLogger(__name__)


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

class _Coder:
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

    def _translate_coordinates(self, x, y, pin, pout):
        '''_translate_coordinates
        Translates vectors of spatial coordinates from one projection to another.
        
        Args:
            x (array-like): Vector of horizontal spatial coordinates.
            y (array-like): Vector of vertical spatial coortinates.
            pin (str): Projection of input vectors.
            pout (str): Output projection.
        
        Returns:
            (tuple of array-like): Translated coordinate vectors.
        '''
        proj_in = pyproj.Proj(pin)
        proj_out = pyproj.Proj(pout)
        return pyproj.transform(proj_in, proj_out, x, y)

    def generate_year_spec(self, year):
        '''generate_year_spec
        '''
        years_available = reversed(sorted(self.shapes.keys())) 
        for y in years_available:
            if year >= y:
                return y
        else:
            return -y


class NutsCoder(_Coder):
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
        fout = os.path.join(self.SHAPE_DIR}, fname)
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
            logger.info(f'Loading NUTS {self.level} {year} boundaries')
            shape_zip_dir = os.path.join(self.SHAPE_DIR, 
                                    f'ref-nuts-{year}-{resolution}m.geojson.zip')
            exists = os.path.isfile(shape_zip_dir)
            if not exists:
                self._get_shape(year)
            z = ZipFile(shape_zip_dir)
            nested = self.NESTED_FILE.format(resolution=resolution, year=year, level=self.level)
            gdf = gpd.read_file(z.open(nested))
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
            y, x = self._translate_coordinates(np.array(x), np.array(y),
                    projection, self.PROJECTION)
        points = self._coordinates_to_points(x, y, data=data)
        joined = self._reverse_geocode(points, year)
        joined = joined.rename(columns={'NUTS_ID': 'nuts_id'})
        return joined


class LepCoder(_Coder):
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
        fout = os.path.join(self.SHAPE_DIR, fname)
        urlretrieve(url, fout)

    def _load_shapes(self):
        self.shapes = {}
        for year, file_url in self.YEAR_URLS.items():
            logger.info(f'Loading LEP {year} boundaries')
            fname = self.FILE.format(year=year)
            shape_dir = os.path.join(self.SHAPE_DIR, fname)
            exists = os.path.isfile(shape_dir)
            if not exists:
                self._get_shape(year, f"{self.TOP_URL}{file_url}")
            gdf = gpd.read_file(shape_dir)
            lep_id_col = f'lep{str(year)[-2:]}cd'
            gdf = gdf.rename(columns={lep_id_col: 'lep_id'})
            self.shapes[year] = gdf


    def code_points(self, x, y, year, projection, data=None):
        """code_points
        """
        shape = self.shapes[year]
        if projection != self.PROJECTION:
            x, y = self._translate_coordinates(np.array(x), np.array(y),
                    projection, self.PROJECTION)
        points = self._coordinates_to_points(x, y, data=data)
        joined = self._reverse_geocode(points, year)
        joined = joined.rename(columns={f'lep{year}cd': 'lep_id'})
        return joined
