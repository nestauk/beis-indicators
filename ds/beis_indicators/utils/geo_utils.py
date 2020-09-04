import geopandas as gpd
import os
import pyproj
from urllib.request import urlretrieve
from zipfile import ZipFile
from beis_indicators.utils.nuts_utils import NUTS_INTRODUCED, NUTS_ENFORCED


def reverse_geocode(points, shape, shape_crs=None):
    '''reverse_geocode

    Args:
        points (pd.DataFrame):
        shape (gpd.GeoDataFrame):
        shape_crs (str): 
    '''
    if shape_crs is not None:
        shape = shape.to_crs(shape_crs)

    joined = gpd.sjoin(points, shape, op='within', how='right')
    return joined


def coordinates_to_points(df, x_coord_name, y_coord_name):
    '''coordinates_to_points
    Take a DataFrame with coordinate columns and returns a GeoDataFrame with 
    a single Point geometry column.
    
    Args:
        df (pandas.DataFrame): A DataFrame with spatial coordinate data.
        x_coord_name (str): Name of the horizontal coordinate column.
        y_coord_name (str): Name of the vertical coordinate column.
        
    Returns:
        (geopandas.GeoDataFrame): GeoDataFrame with Point objects in `geometry` column.
    '''
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_coord_name], df[y_coord_name]))


def translate_coordinates(x, y, pin, pout):
    '''translate_coordinates
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


def load_nuts_regions(year, shapefile_dir, level=2, projection=4326, resolution=1, countries=['UK']):
    '''load_nuts_regions
    Loads NUTS shapefiles.

    Args:
        year (int): NUTS version year.
        shapefile_dir (str): Directory where shapefiles are stored. 
        projection (int): Coordinate projection of shapefile. 
            Choice of EPSG 3035, 3857 or 4326. Default is 4326
        resolution (int): Shapefile resolution in metres.
        countries (list): List of 2 letter country codes to filter by. If None, 
            all regions will be returned. Default is `["UK"]`.
    '''
    
    resolution = str(resolution).zfill(2)

    nuts_dir = (f'{shapefile_dir}/'
                f'ref-nuts-{year}-{resolution}m.shp/'
                f'NUTS_RG_{resolution}M_{year}_{projection}_LEVL_{level}.shp')
    
    if not os.path.isdir(nuts_dir):
        with ZipFile(f'{nuts_dir}.zip','r') as archive:
            archive.extractall(nuts_dir)
        
    nuts_fin = (f'{nuts_dir}/'
                f'NUTS_RG_{resolution}M_{year}_{projection}_LEVL_{level}.shp')
    nuts_gdf = gpd.read_file(nuts_fin)
    
    if countries is not None:
        nuts_gdf = nuts_gdf.set_index('CNTR_CODE').loc[countries].reset_index()
        
    return nuts_gdf


def load_leps_regions(year, shapefile_dir):
    '''load_leps_regions
    Loads LEP shapefiles.
    
    Args:
        year (int): LEP version year.
        shapefile_dir (str): Directory where shapefiles are stored. 
    '''
    year = abs(year)
    if year == 2014:
        fin = 'Local_Enterprise_Partnerships_December_2014_Full_Clipped_Boundaries_in_England'
    elif year == 2017:
        fin = 'Local_Enterprise_Partnerships_April_2017_EN_BFC_V3'
        
    leps_dir = f'{shapefile_dir}/{fin}/{fin}.shp'
    leps_gdf = gpd.read_file(leps_dir)
    return leps_gdf


def leps_year_spec(year):
    '''leps_year_spec
    Return earliest possible year for the LEP boundaries based
    on a given year.
    
    Args:
        year (int): Year of data.
        
    Returns:
        (int): LEP boundary year specification.
    '''
    if year < 2014:
        return -2014
    elif 2014 <= year < 2017:
        return 2014
    elif year >= 2017:
        return 2017
    elif year >= 2020:
        return 2020


def get_nuts_shape(year, shapefile_dir, resolution=1):
    """get_nuts_shape

    Args:
        year (int): NUTS version year. Options are 2021, 2016, 2013,
            2010, 2006 and 2003.
        shapefile_dir (str): Directory where shapefiles are stored. 
        resolution (int): Shapefile resolution in metres. Default is 1.
            Options are 1, 3, 10, 20 and 60.
    """
    
    resolution = str(resolution).zfill(2)

    url = ('http://gisco-services.ec.europa.eu/distribution/'
           f'v2/nuts/download/ref-nuts-{year}-{resolution}m.shp.zip')
    fname = base_url.split('/')[-1]
    fout = f'{shapefile_dir}/{fname}'

    urlretrieve(url, fout)


def get_lep_shape(year):
    """get_lep_shape

    Args:
        year (int): LEP version year. Options are 2020, 2017 and 2014

    """
    with open(f'{project_dir}/data/aux/shapefile_urls.json','r') as infile:
        shape_lookup = json.load(infile)

    url = shape_lookup[f'leps_{year}']
    fname = 'lep_{year}_shp.zip'
    fout = f'{shapefile_dir}/{fname}'
    urlretrieve(url, fout)


def get_shape(file_name, path):
    '''
    Utility function to extract and the shapefile
    
    Arguments:
        url: url for the shapefile zip
        file_name: name of the file where we want to extract the data
    
    '''

    #Do we need to get the data or is it already there?

    shape_names = os.listdir(f'{project_dir}/data/raw/shapefiles')

    if file_name not in shape_names:

        #Get the data
        print(f'getting {file_name}...')

        #Get url
        url = shape_lookup[file_name]

        #Request data
        req = requests.get(url)
        
        #Parse the content
        z = ZipFile(BytesIO(req.content))
        
        #Save
        print(f'saving {file_name}...')
        z.extractall(f'{path}{file_name}')

    else:
        print(f'{file_name} already collected')


def nuts_year_spec(year, mode='introduced'):
    '''nuts_earliest
    Returns the earliest possible NUTS version for a year
    based on the enforcement date.

    Args:
        year (int): A year
        mode (str): Choose whether to map years against the year that a NUTS
            version was enforced or introduced: Options:
                - `introduced` (default)
                - `enforced`
    Returns:
        earliest (int): The closest possible NUTS version year
    '''
    if mode == 'introduced':
        mapping = NUTS_INTRODUCED
    elif mode == 'enforced':
        mapping = NUTS_ENFORCED

    for k, v in mapping.items():
        if year >= v:
            earliest = k
    return earliest


def generate_year_spec(data, geography='nuts', mode='introduced'):
    '''generate_year_spec
    Args:
        data (pd.DataFrame):
        geography (str):
        mode (str):

    Returns:
        year_spec_map (pd.Series):
    '''
    years = data['year'].unique()
    if geography == 'nuts':
        year_spec_map = {y: nuts_year_spec(y, mode) for y in years}
    elif geography == 'lep':
        year_spec_map = {y: leps_year_spec(y) for y in years}
    
    year_spec = data['year'].map(year_spec_map)
    return year_spec
