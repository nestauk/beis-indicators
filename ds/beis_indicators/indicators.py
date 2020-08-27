import os
import geopandas as pd
import pandas as pd
import numpy as np

from beis_indicators.utils.geo_utils import (load_nuts_regions, load_leps_regions,
        generate_year_spec, NUTS_YEARS, LEP_YEARS)


def points_to_indicator(data, value_col, boundaries, geography='nuts',
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
    geo_type = ''.join(i for i in geog if i.isdigit())
    year_spec_col = f'{geo_type}_year_spec'
    id_col = f'{geo_type}_id'
    if year_spec_col not in data.columns:
        data[year_spec_col] = generate_year_spec(data, geo_type)

    if geo_type == 'nuts':
        geo_projection = 'EPSG:4326'
    elif geo_type == 'lep':
        geo_projection = 'EPSG:27700'
    
    if projection != geo_projection:
        data['x'], data['y'] = translate_coordinates(data[x_col].values, 
                data[y_col].values, projection, geo_projection)
    data = coordinates_to_points(data, 'x', 'y')
    
    aggregated = []
    for year, group in data.groupby('year'):
        year_spec = np.abs(group[year_spec_col].max())
        joined = reverse_geocode(group, boundaries[year_spec], geo_projection)
        agg_cols = [id_col, 'year', year_spec_col]
        agg = (joined
                .groupby(agg_cols, asindex=False)[value_col]
                .apply(aggfunc))
        aggregated.append(agg)
    indicator = pd.concat(aggregated)
    
    if value_rename is not None:
        indicator = indicator.rename(columns={value_col: value_rename})
        value_col = value_rename

    indicator = indicator[['year', id_col, year_spec_col, value_col]]
    indicator['year'] = indicator['year'].astype(int)
    indicator[year_spec_col] = indicator[year_spec_col].astype(int)
    if dp is not None:
        indicator[value_col] = np.round(indicator[value_col], dp)
    
    return indicator

def load_regions(geography, years=None, nuts_level=2):
    """load_regions
    Loads regions for a particular geography (and level if required) across 
    multiple years.

    Args:
        geo_type (str): 'nuts' or 'lep'
        years (`iter` of `int`): If None, all possible boundaries will be loaded.
        nuts_level (int): If using geo_type 'nuts' this level will be loaded.

    Returns:
        boundary_pack (dict): A dictionary where keys are years and values are
            `geopandas` dataframes of boundaries.
    """
    geo_type = ''.join(i for i in geog if i.isdigit())
    if years is not None:
        if geo_type == 'nuts':
            years = NUTS_YEARS
        elif geo_type == 'lep':
            years = LEP_YEARS
    
    boundary_pack = {}
    for year in years:
        if geo_type == 'nuts':
            boundaries = load_nuts_regions(year, shapefile_dir, level=level)
        elif geo_type == 'lep':
            boundaries = load_leps_regions(year, shapefile_dir)
        boundary_pack[year] = boundaries
    return boundary_pack
