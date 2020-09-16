import geopandas as gpd


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
