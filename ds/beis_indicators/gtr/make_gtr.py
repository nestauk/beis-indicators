import pandas as pd
import numpy as np
import json
import beis_indicators
from dotenv import load_dotenv

from beis_indicators.utils.dir_file_management import *
from beis_indicators.geo.reverse_geocoder import *
from beis_indicators.hesa.hesa_processing import *

from data_getters.inspector import get_schemas
from data_getters.core import get_engine
from data_getters.labs.core import download_file

def get_gtr(file,file_path,progress=True):
    """ Fetch Gateway To Research predicted industries

    Repo: https://github.com/nestauk/gtr_data_processing
    Commit: cd3cddb
    File: https://github.com/nestauk/gtr_data_processing/blob/master/notebooks/05_jmg_data_demo.ipynb

    Args:
        file_path (`str`, optional): Path to download to. If None, stream file.
        progress (`bool`, optional): If `True` and `file_path` is not `None`,
            display download progress.
    """
    return download_file(file_to_fetch=file, download_path=file_path+file, progress=progress)

def multi_geocode(source_df,lon_lat,ent_id,years):
    '''
    Function that extracts the nuts2 region for a location in multiple years
    
    Args:
        source_df (pandas dataframe) with longitude and latitude we want to geocode
        lon_lat (list) with the names of the longitude and latitude variables
        ent_id (str) is the column we use to identify the entity we are reverse geocoding
        years (str) are the nuts years we want to extract
        
    Returns a dict where the keys are the ids for a place and the values are dicts for different
    nuts years
    '''  
    nutified = [reverse_geocode(place_df=source_df,
                        shape_name=f'nuts2_{str(y)}',
                        shape_file=f'NUTS_RG_01M_{str(y)}_4326_LEVL_2.shp.zip',
                        place_id=ent_id,
                        coord_names= lon_lat)['NUTS_ID'] for y in years]

    #Create a df and turn into a dict
    nutified_df = pd.concat(nutified,axis=1)
    nutified_df.columns = [f"nuts2_{str(y)}" for y in years]
    nutified_dict = nutified_df.to_dict(orient='index')
    
    return(nutified_dict)

#Load the sql credentials to collect data from DAPS
load_dotenv()
sql_creds = os.getenv('config_path')

#Load list of STEM disciplines
with open(f'{project_dir}/data/aux/stem_gtr.txt','r') as infile:
    
    stem = infile.read().split('\n')

#########
#1. COLLECT DATA
#########

#Create connection
con= get_engine(sql_creds)

#1. Collect organisations-locations
orgs_locs = pd.read_sql('gtr_organisations_locations',con=con,chunksize=1000)
orgs_locs_df = pd.concat(orgs_locs)

#2. Collect projects (with discipline predictions and funding) if needed
if os.path.exists(f"{project_dir}/data/raw/gtr/17_9_2019_gtr_projects.csv")==False:
    get_gtr(file='17_9_2019_gtr_projects.csv',file_path=f'{project_dir}/data/raw/gtr/',
            progress=False)

#And then we read it
gtr_proj = pd.read_csv(f'{project_dir}/data/raw/gtr/17_9_2019_gtr_projects.csv',
                      dtype={'id':str})

#Keep relevant variables
gtr_proj_short = gtr_proj[['project_id','year','amount','disc_top']]


#3. Collect link_table connecting orgs to projects
gtr_link = pd.read_sql('gtr_link_table',con=con,chunksize=1000)
gtr_link_df = pd.concat(gtr_link)
link_orgs = gtr_link_df.loc[gtr_link_df['rel']=='LEAD_ORG']

#This is the set of organisations that lead projects
lead_org_id = set(link_orgs['id'])

###########
#2. PROCESS DATA
###########
#Create the org-nuts lookup
#Focus on organisations that lead projects
org_locs_lead = orgs_locs_df.loc[[x in lead_org_id for x in orgs_locs_df['id']]].reset_index(
    drop=False)

#Create the nuts lookup
orgs_nuts = multi_geocode(org_locs_lead,['longitude','latitude'],'id',
                          [2010,2013,2016])

#Merge projects with organisations
proj_org = pd.merge(
    gtr_proj_short,link_orgs[['project_id','id']],
    left_on='project_id',right_on='project_id').query('year >= 2010')


##############
#3. CREATE AND SAVE INDICATORS
##############

# Create the NUTS estimates
nuts_est = multiple_nuts_estimates(proj_org,
                              orgs_nuts,
                              set(proj_org['disc_top']),
                              'disc_top',
                              'amount',
                              year_var='year',my_id='id').fillna(0)

#Create stem discipline aggregation
stem_nuts_est = nuts_est[stem].sum(axis=1)
stem_nuts_est.name = 'total_gtr_projects_stem'

#Make the indicator
ind = make_indicator(stem_nuts_est,{
                     'total_gtr_projects_stem':'total_gtr_projects_stem'},
                    'year')

#Save the indicator
save_indicator(ind,target_path=f'{project_dir}/data/processed/gtr',
               var_name='total_gtr_projects_stem')