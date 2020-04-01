## Logging
import logging
import sys

logger = logging.getLogger()
fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt)

## Import basic scientific stack
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import re
import datetime

import beis_indicators
from beis_indicators.data import make_dataset
from beis_indicators.utils.dir_file_management import *

project_dir = beis_indicators.project_dir
data_path = f'{project_dir}/data'

def extract_segment(path,sector_list,sector_variable,sector_name):
    '''
    This function takes official data from a path and returns a segment of interest.
    We will use it to produce indicators about cultural activities in different NUTS2 regions.
    
    Arguments:
        path (str) is the path we use
        segment (list) is the list of codes we are interested in - could be segments or sectors
        sector_variable (str) is the variable that we use to identify sectors. It could be 
            the sic code or the Nesta segment.
    
    '''
    #Read data
    all_sectors = pd.read_csv(path,dtype={'SIC4':str})
    
    #Activity in sector
    sector = all_sectors.loc[[x in sector_list for x in all_sectors[sector_variable]]].reset_index(
        drop=True)
    
    #Regroup and aggregate
    sector_agg = sector.groupby(['geo_nm','geo_cd','year'])['value'].sum()
    
    #Add the name
    sector_agg.name = sector_name
    
    return(pd.DataFrame(sector_agg))
    
#Cultural industries 
cultural = ['services_cultural','services_recreation','services_entertainment']

##############
#1. Read data
##############

#Read ashe and turn it into a lookup
ashe = pd.read_csv(f'{project_dir}/data/interim/industry/ashe_rankings.csv')

ashe_lookup = ashe.set_index('cluster')['ashe_median_salary_rank'].to_dict()

#bres
bres_2018 = pd.read_csv(f'{project_dir}/data/interim/industry/nomis_BRES_2018_TYPE450.csv',dtype={'SIC4':str},
                       index_col=None)

bres_2018['sal'] = bres_2018['cluster_name'].map(ashe_lookup)

#############
#2. Make indicators
#############

#Cultural employment etc
bres_cult = pd.concat([extract_segment(
    f'{project_dir}/data/interim/industry/nomis_BRES_{y}_TYPE450.csv',cultural,'cluster_name',
    'culture_entertainment_recreation') for y in [2016,2017,2018]])

make_indicator(bres_cult,
               'industry',
               {'culture_entertainment_recreation':'employment_culture_entertainment_recreation'},year_var='year',
              nuts_spec=2013,nuts_var='geo_cd',decimals=0)

#Economic complexity based on IDBR data
compl= pd.read_csv(f'{project_dir}/data/interim/industry/nomis_ECI.csv')

make_indicator(compl.loc[compl['source']=='IDBR'],
              'industry',
              {'eci':'economic_complexity_index'},year_var='year',nuts_spec=2013,nuts_var='geo_cd',
              decimals=4)



    
    