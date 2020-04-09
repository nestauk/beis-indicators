import geopandas as gpd
import os
import pyproj


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
