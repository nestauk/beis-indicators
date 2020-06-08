#!/usr/bin/env python

import click
from collections import defaultdict
from datetime import datetime
import json
import os
import pandas as pd
import yaml


from beis_indicators import project_dir
from beis_indicators.utils.nuts_utils import NUTS_ENFORCED, load_nuts_regions


@click.command()
@click.option('--test', type=bool, help='Output test readme', default=True)
def generate(test):
    processed_dir = f'{project_dir}/data/processed/'

    dfs = list(generate_indicator_tables(processed_dir))
    df = pd.concat(dfs, axis=0)

    df = apply_nuts_codes(df)
    
    date = time_now()
    if test:
        fout = f'{processed_dir}/all_indicators_test_{date}.csv'
    else:
        fout = f'{processed_dir}/all_indicators_{date}.csv'

    df.to_csv(fout, index=False)


def load_types():
    with open(f'{project_dir}/data/schema/types.yaml', 'r') as f:
        types = yaml.safe_load(f.read())
    return types


def get_unit_string(indicator_schema):
    '''get_unit_string
    '''
    types = load_types()
    unit_type = indicator_schema['unit']
    if unit_type == 'int':
        return 'integer'
    elif unit_type is not None:
        return types[unit_type]['unit_string']
    else:
        return indicator_schema['label']


def generate_indicator_tables(processed_dir):
    subdirs = list_subdirs(processed_dir)
    for subdir in subdirs:
        files = os.listdir(subdir)
        indicator_dirs = []
        schema_dirs = []
        skips = [
#                 'broadband', 
#                 'total_inventions',
#                 'total_active_graduate_startups',
#                 'gbp_turnover_per_active_spinoff',
#                 'gbp_investment_per_active_spinoff',
                ]
        for f in files:
            f = os.path.join(subdir, f)
            if ('.nuts3.' in f) or ('.lep.' in f):
                continue
            elif any([True if s in f else False for s in skips ]):
                continue
            else:
                if '.csv' in f:
                    indicator_dirs.append(f)
                elif '.yaml' in f:
                    schema_dirs.append(f)
#         indicator_dirs = [
#                 os.path.join(subdir, f) for f in files 
#                 if f[-9:] == 'nuts2.csv']
#         schema_dirs = [
#                 os.path.join(subdir, f) for f in files 
#                 if f[-10:] == 'nuts2.yaml']

        for indicator, schema in zip(indicator_dirs, schema_dirs):
            yield create_indicator_table(indicator, schema)


def get_var_name(df):
    drops = ['nuts_id', 'nuts_year_spec', 'year']
    col = [c for c in df.columns if c not in drops]
    return col[0]


def create_indicator_table(indicator_dir, schema_dir):

    df = pd.read_csv(indicator_dir)
    
    with open(schema_dir, 'r') as f:
        schema = yaml.safe_load(f.read())
        schema = parse_schema(schema)

    var_name = get_var_name(df) 
    df['variable'] = var_name
    
    df['description'] = schema['title']

    unit = get_unit_string(schema)
    df['unit'] = unit

    df = df.rename(columns={var_name: 'value', 'nuts_year_spec': 'nuts_year'})

    return df


def apply_nuts_codes(df):
    nuts = {}
    for year in NUTS_ENFORCED.keys():
        regions = load_nuts_regions(
                    year, 
                    f'{project_dir}/data/raw/shapefiles',
                    level=2,
                    resolution=20,
                    )
        code_name_map = {}
        for code, name in zip(regions['NUTS_ID'].values, regions['NUTS_NAME'].values):
            code_name_map[code] = name
        nuts[year] = code_name_map

    def map_nuts_codes(year, code, var):
        return nuts[year][code]

    df['nuts_name'] = df.apply(
            lambda row: map_nuts_codes(row['nuts_year'], row['nuts_id'], row['variable']),
            axis=1
            )
    return df


def time_now():
    now = datetime.utcnow()
    now = datetime.strftime(now, format='%Y-%M-%d')
    return now


def parse_schema(schema):
    '''parse_schema
    Extracts, formats and returns field content for each indicator entry in 
    readme.
    '''
    value = schema['schema']['value']
    if 'type' in value:
        unit = value['type']
    else:
        unit = None

    readme_fields = dict(
        title=value['description'],
        source=schema['source_name'],
        long_description=schema['description'],
        unit=unit,
        label=value['label']
        )
    return readme_fields


def list_subdirs(dir):
    '''list_subdirs
    Returns a list of sub directory names that exist within dir.
    '''
    paths = [os.path.join(dir, p) for p in os.listdir(dir)]
    subdirs = [p for p in paths if os.path.isdir(p)]
    return subdirs

if __name__ == "__main__":
    generate()
