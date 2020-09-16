import os
import requests
import pandas as pd
import eurostat as es
from zipfile import ZipFile
from io import BytesIO
import beis_indicators
import logging
from beis_indicators.utils.dir_file_management import make_indicator,save_indicator

PROJECT_DIR = beis_indicators.project_dir
TARGET_PATH = f"{PROJECT_DIR}/data/processed/eurostat"

# We need to collect NUTS tables for 2010 (patents) and 2013 (trademarks)
nuts_codes = {'2010':{},'2013':{}}

# Only get the data if we don't have it already
for y in ['2010','2013']:
    file = f'NUTS_{y}.xls'
    if os.path.exists(f'{PROJECT_DIR}/data/aux/{file}')==False:
        nuts = requests.get(
            'https://ec.europa.eu/eurostat/ramon/documents/nuts/NUTS_{y}.zip')
        z = ZipFile(BytesIO(nuts.content))
        z.extract(file,path=f'{PROJECT_DIR}/data/aux/')

    nuts_table = pd.read_excel(f'{PROJECT_DIR}/data/aux/{file}')

    for l in [2,3]:
        nuts_codes[y][l]=set(
            nuts_table.loc[(nuts_table['COUNTRY CODE']=='UK')&(
                                nuts_table['NUTS LEVEL']==l)]['NUTS CODE'])

# Collect the patent and trademark data from Eurostat
pats = es.get_data_df('pat_ep_rtot').query("unit == 'NR'")
trades = es.get_data_df('ipr_ta_reg')

# For each NUTS codes list and name
for nuts_level,level in zip([2,3],['nuts2','nuts3']):
    
    # For each table and variable name
    for d,name in zip([pats,trades],
                      ['epo_patent_applications','eu_trademark_applications']):
        
        # Extract nuts codes depending on the variable (patents are 2010)
        if 'patent' in name:
            nuts_list = nuts_codes['2010'][nuts_level]
        else:
            nuts_list = nuts_codes['2013'][nuts_level]
            
        # Select the data. We will focus on activity after 2005
        sel = d.loc[
            [x in nuts_list for x in d['geo\\time']]].reset_index(
            drop=True).drop('unit',1).melt(id_vars='geo\\time').query(
            "variable > 2005")
        
        # Make indicator
        if 'patent' in name:
            nuts_spec =2010
        else:
            nuts_spec =2013

        ind = make_indicator(sel,{'value':name},year_var='variable',nuts_var='geo\\time',
                    nuts_spec=nuts_spec)
    
        logging.info(str(min(ind['year'])))
        logging.info(str(max(ind['year'])))
        
        # Save indicator
        save_indicator(ind,TARGET_PATH,f"{name}.{level}")
    