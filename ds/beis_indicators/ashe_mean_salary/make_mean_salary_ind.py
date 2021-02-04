import pandas as pd
import requests
import os
import beis_indicators
from beis_indicators.utils.dir_file_management import make_indicator,save_indicator


PROJECT_DIR = beis_indicators.project_dir
INTERIM_PATH = f"{PROJECT_DIR}/data/interim/ashe_mean_salary"
TARGET_PATH = f"{PROJECT_DIR}/data/processed/ashe_mean_salary"


# Get the LAD to NUTS lookup
lad_nuts_lu = pd.read_csv(
    "https://opendata.arcgis.com/datasets/9b4c94e915c844adb11e15a4b1e1294d_0.csv")

# Create mean salaries by NUTS

# Get mean LAD salaries from ASHE (Annual Survey of Hours and Earnings)
lads_ashe = pd.read_csv(
    "https://www.nomisweb.co.uk/api/v01/dataset/NM_30_1.data.csv?geography=1820327937...1820328307&date=latestMINUS9-latest&sex=8&item=4&pay=7&measures=20100,20701")
# Get employment levels
lads_bres = pd.read_csv(
    "https://www.nomisweb.co.uk/api/v01/dataset/NM_189_1.data.csv?geography=1820327937...1820328307&date=latest&industry=37748736&employment_status=2&measure=1&measures=20100")

# These are the variables we are interested in
my_vars = ['DATE','GEOGRAPHY_NAME','GEOGRAPHY_CODE','OBS_VALUE']

# This filters each of the tables we downloaded and renames variables
lads_ashe, lads_bres = [df.query("MEASURES_NAME == 'Value'")[my_vars].reset_index(
   drop=True).rename(columns={'OBS_VALUE':var_name}) for
        df, var_name in zip([lads_ashe,lads_bres],
                       ['annual_mean_salary_ft','employees_ft'])]

# Combine them
merge_vars = ['GEOGRAPHY_NAME','GEOGRAPHY_CODE','DATE']

ashe_bres = pd.merge(lads_ashe,lads_bres,left_on=merge_vars,
                     right_on=merge_vars)

# Multiply mean salary by full time employees so we can get the local wage bill
ashe_bres['wage_bill'] = ashe_bres['annual_mean_salary_ft']*ashe_bres[
                    'employees_ft']

# Before merging with the LAD-NUTS lookup we need to relabel some LADs in
# the lookup

# More info here https://hub.arcgis.com/datasets/c3ddcd23a15c4d7985d8b36f1344b1db)
recodes = {'Glasgow City':'S12000049',
          'Bournemouth':'E06000058',
          'Christchurch':'E06000058',
          'Poole':'E06000058',
          'Suffolk Coastal':'E07000244',
          'Waveney':'E07000244',
          'Forest Heath':'E07000245',
          'St Edmundsbury':'E07000245',
          'Taunton Deane':'E07000246',
          'West Somerset':'E07000246',
           'East Dorset':'E06000059',
           'West Dorset':'E06000059',
           'North Dorset':'E06000059',
           'North Lanarkshire':'S30000023'}

# Relabel codes
lad_nuts_lu['LAD18CD+'] = [r['LAD18CD'] if r['LAD18NM'] not in recodes.keys() else
                            recodes[r['LAD18NM']] for
                          _id,r in lad_nuts_lu.iterrows()]

# Merge LAD economic info with the LAD to NUTS lookup
nuts_look_nomis = pd.merge(
            lad_nuts_lu,ashe_bres,left_on='LAD18CD+',right_on='GEOGRAPHY_CODE')


# And now calculate the NUTS2 and NUTS3 mean salaries
# Create the mean salaries by NUTS 2 and NUTS 3

nuts_2_mean_salary, nuts_3_mean_salary = [
    nuts_look_nomis.groupby(
            ['DATE',code])[['employees_ft','wage_bill']].sum(
            ).reset_index(
                drop=False).assign(
                mean_salary = lambda x:
                    x['wage_bill']/x['employees_ft']) for code in [
                            'NUTS218CD','NUTS318CD']]

#Save interim data for housing affordability calculation

for mean_salary_df, file_name in zip([nuts_2_mean_salary, nuts_3_mean_salary],
                            ['nuts_2_mean_salary', 'nuts_3_mean_salary']):
    save_indicator(mean_salary_df,INTERIM_PATH,f'{file_name}')

# Make the indicator

for sal,code,suffix in zip([nuts_2_mean_salary,nuts_3_mean_salary],
                             ['NUTS218CD','NUTS318CD'],
                             ['nuts2','nuts3']):

    #Make indicator
    ind = make_indicator(sal,
                         {'mean_salary':'ashe_mean_salary'},
                        'DATE',nuts_var=code,nuts_spec=2018,decimals=3)

    #Save the indicator
    save_indicator(ind,TARGET_PATH,f'ashe_mean_salary.{suffix}')
