import geopandas as gpd
import os
from urllib.request import urlretrieve
from zipfile import ZipFile
from beis_indicators.utils.nuts_utils import NUTS_INTRODUCED, NUTS_ENFORCED


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


