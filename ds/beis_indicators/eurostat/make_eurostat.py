import logging
import numpy as np
import pandas as pd
import glob
import ast

from eurostatapiclient import EurostatAPIClient
from beis_indicators.geo.nuts import auto_nuts2_uk
from beis_indicators import project_dir

logger = logging.getLogger(__name__)

VERSION = 'v2.1'
FORMAT = 'json'
LANGUAGE = 'en'
client = EurostatAPIClient(VERSION, FORMAT, LANGUAGE)

vars_map = {
    'EUR_HAB': 'Euro per inhabitant',
    'MIO_EUR': 'Million euro',
    'FTE': 'Full-time equivalent (FTE)',
    'HC': 'Head count',
    'PC_ACT_FTE': 'Percentage of active population - numerator in full-time equivalent (FTE)',
    'PC_ACT_HC': 'Percentage of active population - numerator in head count (HC)',
    'PPS_HAB': 'Purchasing power standard (PPS) per inhabitant'
}


def make_indicator(query, indicator):
    df = client.get_dataset(query)
    df = df.to_dataframe()

    df['time'] = df['time'].astype(int)

    df = df.pivot_table(index=['geo','time'],
               columns = 'unit',
               values = 'values').reset_index().set_index('geo')

    if 'MIO_EUR' in df.columns:
        df['euros'] = df['MIO_EUR'] * 1000000.00
        df.drop(columns=['MIO_EUR'], inplace=True)
    elif 'PPS_HAB' in df.columns:
        df['PPS_HAB'] = df['PPS_HAB'].round(2)
    elif 'HC' in df.columns:
        df['HC'] = pd.to_numeric(df['HC'], downcast='integer')


    df.reset_index(inplace=True)
    df.columns = ['nuts_id', 'year', indicator]
    df = auto_nuts2_uk(df)

    df = df[['year','nuts_id', 'nuts_year_spec', indicator]]

    return df

with open(f'{project_dir}/data/aux/eurostat_data_queries.txt', 'r') as f:
    mylist = ast.literal_eval(f.read())



for dataset in mylist:

    df = make_indicator(dataset['query'], dataset['indicator'])

    df.to_csv(f'../../data/processed/eurostat/{dataset['indicator']}.nuts2.csv', index=False)
