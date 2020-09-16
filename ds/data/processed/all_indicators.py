#!/usr/bin/env python

import click
from collections import defaultdict
from datetime import datetime
import json
import os
import pandas as pd
import numpy as np
import yaml


from beis_indicators import project_dir
from beis_indicators.geo import NutsCoder, LepCoder


@click.command()
@click.option('--test', type=bool, help='Output test readme', default=True)
@click.option('--geography', type=str, help='One of lep, nuts2 or nuts3', default='nuts2')
def generate(test, geography):
    processed_dir = f'{project_dir}/data/processed/'

    dfs = list(generate_indicator_tables(processed_dir, geography))
    df = pd.concat(dfs, axis=0)
    
    if 'nuts' in geography:
        level = int(geography[-1])
        df = apply_nuts_codes(df, level=level)
    elif 'lep' in geography:
        df = apply_lep_codes(df)
    
    date = time_now()
    if test:
        fout = f'{processed_dir}/all_indicators_test_{date}.{geography}.csv'
    else:
        fout = f'{processed_dir}/all_indicators_{date}.{geography}.csv'

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


def skip_by_geography(fname, geography):
    if f'.{geography}.' in fname:
        return False
    elif geography == 'nuts2':
        if ('.nuts3.' in f) or ('.lep.' in f):
            return True
        else:
            return False
    else:
        return True


def generate_indicator_tables(processed_dir, geography):
    subdirs = list_subdirs(processed_dir)
    for subdir in subdirs:
        files = os.listdir(subdir)
        indicator_dirs = []
        schema_dirs = []
        skips = []
        for f in files:
            f = os.path.join(subdir, f)
            if skip_by_geography(f, geography):
#             if ('.nuts3.' in f) or ('.lep.' in f):
                continue
            elif any([True if s in f else False for s in skips ]):
                continue
            else:
                if '.csv' in f:
                    indicator_dirs.append(f)
                elif '.yaml' in f:
                    schema_dirs.append(f)

        for indicator, schema in zip(indicator_dirs, schema_dirs):
            yield create_indicator_table(indicator, schema, geography)


def strip_geography(geography):
    if 'nuts' in geography:
        return 'nuts'
    elif 'lep' in geography:
        return 'lep'


def get_var_name(df, geo):
    drops = [f'{geo}_id', f'{geo}_year_spec', 'year']
    col = [c for c in df.columns if c not in drops]
    return col[0]


def create_indicator_table(indicator_dir, schema_dir, geography):
    geo = strip_geography(geography)

    df = pd.read_csv(indicator_dir)
    
    with open(schema_dir, 'r') as f:
        schema = yaml.safe_load(f.read())
        schema = parse_schema(schema)

    var_name = get_var_name(df, geo) 
    df['variable'] = var_name
    
    df['description'] = schema['title']

    unit = get_unit_string(schema)
    df['unit'] = unit

    df = df.rename(columns={var_name: 'value', f'{geo}_year_spec': f'{geo}_year'})
    try:
        df = df[[f'{geo}_id', f'{geo}_year', 'year', 'value', 'variable', 'description', 'unit']]
    except:
        print(schema_dir)

    return df


def apply_nuts_codes(df, level):
    nuts = {}
    nuts_coder = NutsCoder(level=level)
    for year, regions in nuts_coder.shapes.items():
        code_name_map = {}
        for code, name in zip(regions['NUTS_ID'].values, regions['NUTS_NAME'].values):
            code_name_map[code] = name
        nuts[year] = code_name_map

    def map_nuts_codes(year, code, var):
        year = np.abs(year)
        return nuts[year][code]

    df['nuts_name'] = df.apply(
            lambda row: map_nuts_codes(row['nuts_year'], row['nuts_id'], row['variable']),
            axis=1
            )
    return df


def apply_lep_codes(df):
    leps = {}
    lep_coder = LepCoder()
    for year, regions in lep_coder.shapes.items():
        lep_year = str(year)[-2:]
        name_col = f'lep{lep_year}nm'
        code_name_map = {}
        for code, name in zip(regions['lep_id'].values, regions[name_col].values):
            code_name_map[code] = name
        leps[year] = code_name_map

    def map_lep_codes(year, code, var):
        year = np.abs(year)
        return leps[year][code]

    df['lep_name'] = df.apply(
            lambda row: map_lep_codes(row['lep_year'], row['lep_id'], row['variable']),
            axis=1
            )
    return df


def time_now():
    now = datetime.utcnow()
    now = datetime.strftime(now, format='%Y-%m-%d')
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
