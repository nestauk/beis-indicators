import logging
import pandas as pd
import numpy as np
import os

from beis_indicators import project_dir


def points_to_indicator(data, value_col, coder, 
        aggfunc=np.mean, value_rename=None, projection=None, 
        x_col='lon', y_col='lat', dp=2, fillna=0):
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
        coder (Coder): A coder object
        aggfunc (function): Function used to aggregate points within a boundary.
            Default is `np.mean`.
        value_rename (str): Optional. If provided, then the value column will be
            renamed as this for the output indicator.
        projection (str): Geographic projection of the data. Projections might
            include:
                - British coordinates: 'EPSG:27700'
                - Latlon: 'EPSG:4326'
        x_col (str): Column of the x coordinate.
        y_col (str): Column of the y coordinate.
        dp (int): Decimal places to round the final indicator values to. If 
            None, rounding will not be applied.
        fillna (str or int): A value to be used to fill in any missing data
            for regions in the final indicator. If None, then the region 
            will be present with a NaN value.

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
    year_spec_map = {year: coder.generate_year_spec(year) 
            for year in data['year'].unique()}
    data[year_spec_col] = data['year'].map(year_spec_map)
    
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
    if fillna is not None:
        indicator[value_col].fillna(fillna, inplace=True)
    if dp is not None:
        indicator[value_col] = np.round(indicator[value_col], dp)
    
    return indicator


def save_indicator(data, folder, region_type, schema=False):
    '''
    Function to save an indicator

    Args:
        data (pandas.DataFrame): A finalised indicator dataframe.
        folder (str): The name of the sub-directory within data/processed
            where the data will be stored. If this doesn't exist, it will
            be created.
        region_type (str): Suffix for the region type. This will probably be 
            one of nuts2, nuts3 or lep.
        schema (bool): If True, a partially filled schema will be generate and 
            saved. Defaults to False. 
            WARNING: if True, any existing schema be overwritten.

    '''
    n_cols = data.columns.shape[0]
    if len(data.columns) != 4:
        raise ValueError(f'Data should have 4 columns. This has {n_cols}.')

    folder = f'{project_dir}/data/processed/{folder}'
    if not os.path.isdir(folder):
        os.mkdir(folder)

    id_col = f'{region_type[:4]}_id'
    year_spec_col = f'{region_type[:4]}_year_spec'
    name = list(filter(lambda x: x not in ['year', id_col, year_spec_col], data.columns))[0]

    data.to_csv(f'{folder}/{name}.{region_type}.csv', index=False)

    if schema == True:
        generate_schema(data, name, region_type)


def generate_schema(data, name, region_type):
    pass
