import pandas as pd 
import numpy as np
import requests
import beis_indicators
import os
import logging
from beis_indicators.utils.dir_file_management import make_indicator, save_indicator

project_dir = beis_indicators.project_dir

# Create target directory to save indicator

target_path = f'{project_dir}/data/processed/migration'

if os.path.exists(target_path)==False:
    os.mkdir(target_path)

logging.info("Collecting data")
# We get a 403 when we try to open directly with pandas so we save it in raw 
# & load it

file = requests.get(
    "https://www.ons.gov.uk/file?uri=%2fpeoplepopulationandcommunity%2fpopulationandmigration%2fmigrationwithintheuk%2fdatasets%2flocalareamigrationindicatorsunitedkingdom%2fcurrent/lamis2020final.xlsx")

#Save it
with open(f'{project_dir}/data/raw/migration.xls','wb') as outfile:
    outfile.write(file.content)

# Read the file
migration = pd.read_excel(f'{project_dir}/data/raw/migration.xls',sheet_name=1,header=None)

logging.info("Processing data")

migration.fillna(method='ffill',axis=1,inplace=True)

# Join the first three values in each column to create a variable 
# with information about year, variable and direction
col_name = migration.loc[:2].fillna('').apply(lambda x: '__'.join(list(x)))

# Remove the four first redundant rows
migration_2 = migration.loc[4:]

migration_2.columns = col_name 

# Melt using the LAD names / codes as id_vars
migration_long = pd.melt(migration_2,id_vars=migration_2.columns[:2])

# Drop missing rows
migration_long.dropna(axis=0,subset=['Area Code____'],inplace=True)

# Period contains the year, variable 2 the name and 
# direction whether it is inflow or outflow
migration_long['period'],migration_long['variable_2'],migration_long['direction'] = [
    [var.split('__')[n] for var in migration_long['variable']] for n in [0,1,2]]

# Rename variables
migration_long['period'] = [int(
                x.strip().split('-')[-1])-1 for x in migration_long['period']]

migration_long['variable_2'] = [
        'population_estimate' if 'Population' in x else 'internal_migration' if 'Internal' in x
        else 'international_migration' for x in migration_long['variable_2']]

migration_long['direction'] = [np.nan if len(x)==0 
                else x.lower() for x in migration_long['direction']]

# Keep cleanish variable names
migration_clean = migration_long[
        ['Area Code____','Area Name____','period','variable_2','direction','value']]

migration_clean.rename(
            columns={'Area Code____':'area_code',
            'Area Name____':'area_name'},inplace=True)

# Rearrange to normalise by population
# We merge the pop estimate part of the data frame with the migration measure
migration_rearranged = pd.merge(
        migration_clean.loc[migration_clean['variable_2']=='population_estimate'],
        migration_clean.loc[migration_clean['variable_2']!='population_estimate'],
                left_on=['area_code','area_name','period'],
                right_on=['area_code','area_name','period'])

# We rename some repeated variable names
migration_rearranged.rename(columns={
                            'value_x':'population_estimate',
                            'variable_2_y':'variable',
                            'direction_y':'direction',
                            'value_y':'value'},inplace=True)

# Remove a few observations with no codes
migration_rearranged= migration_rearranged.loc[
        [len(x)>2 for x in migration_rearranged['area_code']]]

logging.info("Converting to NUTS")
# We will do LADS to NUTS via the NSPL and then across multiple NUTS
# through a ONS lookup

nspl = pd.read_csv(f'{project_dir}/data/raw/nspl/Data/NSPL_FEB_2020_UK.csv')

#Get the LAD to NUTS rows
laua_nuts = nspl.drop_duplicates(
                'nuts').reset_index(drop=True)[['laua','nuts']]

# Get the lad to many different nuts lookup
lad_nuts_lookup = pd.read_csv(
        'https://opendata.arcgis.com/datasets/10abfc7a2fb249caa13ed345fe756e4e_0.csv')

# Create the lad to nuts lookup
new_lookup = pd.merge(laua_nuts,lad_nuts_lookup,
                      left_on='nuts',right_on='LAU218CD')[
                        ['laua','LAU118NM',
                        'NUTS218CD','NUTS218NM','NUTS318CD','NUTS318NM']]

logging.info("Saving indicators")
for n in [2,3]:
    # Create the lad to nuts leve lookup
    nuts_lookup = new_lookup.drop_duplicates('laua').reset_index(
        drop=True)[['laua',f'NUTS{n}18CD',f'NUTS{n}18NM']]
    
    # Merge migration data and NUTS
    migration_w_nuts = migration_rearranged.merge(
                            new_lookup,left_on='area_code',right_on='laua')
    
    # Regroup by NUTS and aggregate population estimate and migration
    migration_regrouped = migration_w_nuts.groupby(
                [f'NUTS{n}18NM',f'NUTS{n}18CD','direction','variable','period'])[
    ['population_estimate','value']].sum().reset_index(drop=False)
    
    # Rename variables
    migration_regrouped.rename(
                columns={f'NUTS{n}18NM':'nuts_name',
                f'NUTS{n}18CD':'nuts_code'},inplace=True)
    
    # We want to create a different indicator for each type of migration
    for v in ['internal_migration','international_migration']:
        
        name = v.split('_')[0]
        
        migration_selected = migration_regrouped.query(f"variable=='{v}'")
        
        migration_wide = migration_selected.pivot_table(
            index=['nuts_name','nuts_code','period','population_estimate'],
            columns='direction',values='value',aggfunc='sum').reset_index(drop=False)
         
        migration_wide['net'] = 1000*(
            migration_wide['inflow']-migration_wide['outflow'])/migration_wide[
        'population_estimate']
    
        ind = make_indicator(migration_wide,{
                             'net':f'net_migration_rate_{name}'},
                             year_var='period',
                             nuts_var='nuts_code',nuts_spec=2016,
                             decimals=2)
    
        save_indicator(ind,target_path,f'net_migration_rate_{name}.nuts{n}')