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
NUTS_FILE = 'NUTS_2013.xls'

# Collect a table with NUTS names and codes
nuts = requests.get(
        'https://ec.europa.eu/eurostat/ramon/documents/nuts/NUTS_2013.zip')

# Unzip and save
z = ZipFile(BytesIO(nuts.content))

if os.path.exists(f'{PROJECT_DIR}/data/aux/{NUTS_FILE}')==False:
    z.extract(file,path=f'{PROJECT_DIR}/data/aux/')

# Extract NUTS codes
nuts_2013 = pd.read_excel(f'{PROJECT_DIR}/data/aux/{NUTS_FILE}')

nuts_2,nuts_3 = [
        set(nuts_2013.loc[(nuts_2013['COUNTRY CODE']=='UK'
                           )&(nuts_2013['NUTS LEVEL']==l)]['NUTS CODE']) 
                 for l in [2,3]]

# Collect the patent and trademark data from Eurostat
pats = es.get_data_df('ipr_ta_reg')
trades = es.get_data_df('ipr_ta_reg')

# For each NUTS codes list and name
for nuts_list,level in zip([nuts_2,nuts_3],['nuts2','nuts3']):
    
    # For each data source and indicator name
    for d,name in zip([pats,trades],
                      ['epo_patent_applications','eu_trademark_applications']):
        # Filter by NUTS codes
        sel = d.loc[
            [x in nuts_list for x in pats['geo\\time']]].reset_index(
            drop=True).drop('unit',1).melt(id_vars='geo\\time')
        # Create indicator
        ind = make_indicator(sel,{'value':name},
                             year_var='variable',
                             nuts_var='geo\\time',
                             nuts_spec=2013)
        # Print years (for the schema)
        logging.info(ind['year'].min())
        logging.info(ind['year'].max())

        # Save indicator
        save_indicator(ind,TARGET_PATH,f"{name}.{level}")