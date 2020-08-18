import pandas as pd
import requests
import os
import beis_indicators
from beis_indicators.utils.dir_file_management import make_indicator,save_indicator


PROJECT_DIR = beis_indicators.project_dir
TARGET_PATH = f"{PROJECT_DIR}/data/processed/housing"


# Get the LAD to NUTS lookup
lad_nuts_lu = pd.read_csv(
    "https://opendata.arcgis.com/datasets/9b4c94e915c844adb11e15a4b1e1294d_0.csv")

# PART 1: Create mean salaries by NUTS

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

# PART 2: House affordability

# Download house pricing index data
hpi = pd.read_csv(
        'http://publicdata.landregistry.gov.uk/market-trend-data/house-price-index-data/UK-HPI-full-file-2020-03.csv?utm_medium=GOV.UK&utm_source=datadownload&utm_campaign=full_fil&utm_term=9.30_20_05_20')

# We focus on these variables
hpi_short = hpi[['Date','RegionName','AreaCode','AveragePrice','SalesVolume']]

# Create a year variable
hpi_short['year'] = hpi['Date'].apply(lambda x: int(x.split('/')[-1]))

# Focus on 2010-2019 (we don't have 2020 data for the denominator)
# Like before we will create a value data we use to recalculate means at NUTS level
hpi_short = hpi_short.query(
    "(year >= 2010) & (year < 2020)").assign(
    sales_value = lambda x: x.AveragePrice * x.SalesVolume)

# Now we need to create a NUTS3 and NUTS2 lookup like before
nuts_look_hpi = pd.merge(lad_nuts_lu,hpi_short,
                        left_on='LAD18CD+',right_on='AreaCode')

nuts_2_mean_hp, nuts_3_mean_hp = [
    nuts_look_hpi.groupby(
        ['year',code])[['sales_value','SalesVolume']].sum().reset_index(
        drop=False).assign(
                        mean_hp = lambda x: x['sales_value']/x['SalesVolume']
                        ) for code in ['NUTS218CD','NUTS318CD']]

# Create the indicatoes by combining salary and house price data at the
# right level. We also include variable and indicator names in the loop
for sal,med,code,suffix in zip([nuts_2_mean_salary,nuts_3_mean_salary],
                             [nuts_2_mean_hp,nuts_3_mean_hp],
                             ['NUTS218CD','NUTS318CD'],
                             ['nuts2','nuts3']):
    # Merge salaries and house prices
    m = sal.merge(med,left_on=['DATE',code],
            right_on=['year',code]).assign(house_price_norm = 
            lambda x: x['mean_hp']/x['mean_salary'])
    
    # Make the indicator
    ind = make_indicator(m,
                         {'house_price_norm':'house_price_normalised'},
                        'year',nuts_var=code,nuts_spec=2015,decimals=3)
    
    # Save the indicator
    save_indicator(ind,TARGET_PATH,f'house_price_normalised.{suffix}')