import os
import re
import json
from data_getters.labs.core import download_file
from data_getters.core import get_engine
from ast import literal_eval
import pandas as pd

import beis_indicators
from beis_indicators.geo.reverse_geocoder import reverse_geocode
from beis_indicators.utils.dir_file_management import *
from beis_indicators.utils.nesta_utils import get_daps_data
from dotenv import load_dotenv

from forex_python.converter import CurrencyRates
c = CurrencyRates()

project_dir = beis_indicators.project_dir

#Get config path to work with daps data
load_dotenv()

conf_path = os.environ.get('config_path')

def make_conversion(x,tid):
    '''

    Function to convert funding rounds from CrunchBase into GBP
    Args:
        transaction: a transaction from the CB funding rounds dataset
        tid: transaction id (to track issues)
    Returns:
        A conversion (if possible)
    '''
    #If an amount is not in GBP convert to GBP, if not, keep it as is
    
    #The currency converter doesn't work with Lebanese pounds so we will skip that
    
    if (x['raised_amount_currency_code']=='LBP')|(x['raised_amount_currency_code']==None):
        return(np.nan)
    else:
        try:
            out = x['raised_amount']*c.get_rate(
                x['raised_amount_currency_code'],'GBP',x['announced_on']) if 
                    x['raised_amount_currency_code']!='GBP' else x['raised_amount']
            return(out)

        except: 
            print(tid)

def aggregate_investments(df,geography):
    '''
    This function aggregates level of funding over a geography and investment type for a selected period
    
    Arguments:
        df: df with investment levels by geocoded organisaton, year and type
        years: (list) year range to be considered
        geography: (str) what geography name to use
    
    Returns a table where the rows are the geography and the columns are 
    levels of funding by investment type
    
    '''
    
    #Pivot
    out = pd.pivot_table(df,index=[geography,'year'],columns='investment_type',
                         values='raised_amount_gbp',aggfunc='sum').fillna(0)
    
    return(out)

def add_nuts_label(df,location_id,nuts_lookup,method):
    '''
    Add the nuts label to each company.
    Args:
        cb_df (pandas.DataFrame) is a crunchbase organisation df
        location_id (str) is the id for a location
        nuts_lookup (dict) is a lookup between location_id and nuts
        method (str) is whether we are creating the indicator using a time 
        consistent approach 
            (each year in its NUTS category) or using the latest nuts
    '''
    df_2 = df.copy()

    if method == 'time_consistent':
        df_2['nuts_code'] = [nuts_lookup[row['location_id']][get_nuts_category(
                                row['year'])] 
            if row['location_id'] in nuts_lookup.keys() else 
            np.nan for rid,row in df_2.iterrows()]
    else:
        df_2['nuts_code'] = [nuts_lookup[row['location_id']]['nuts2_2016'] if 
            row['location_id'] in nuts_lookup.keys() else 
            np.nan for rid,row in df_2.iterrows()]

    return(df_2)

############
#1. Data and metadata 
############

#Read geocoded nuts
with open(f"{project_dir}/data/interim/cb_geos.json", 'r') as infile:
    cb_nuts = json.load(infile)

# Download CrunchBase data using DAPS
#Create connection with SQL
con =  get_engine(conf_path)

#Read org data
#Read funding rounds
cb_funding_rounds = get_daps_data('crunchbase_funding_rounds',con)

############
#2. Process
############
#Geocode investments
#Focus on recent investments in the UK
cb_funding_rounds['year'] = [x.year for x in cb_funding_rounds['announced_on']]

cb_funding_recent = cb_funding_rounds.loc[
        cb_funding_rounds['year']>=2010]

cb_funding_rounds_uk = cb_funding_recent.loc[
        cb_funding_recent['country']=='United Kingdom']

inv_geo = add_nuts_label(cb_funding_rounds_uk,
                         'location_id',cb_nuts,method='time_consistent')

#Currency conversion
#If an amount is not in GBP convert to GBP, if not, keep it as is
inv_geo['raised_amount_gbp'] = [make_conversion(x,rid) for rid,x in inv_geo.iterrows()]

#Use the indicators_w_threshold function to calculate levels of investment by NUTS area
inv_nuts2 = aggregate_investments(inv_geo,'nuts_code')

#Focus on venture capital - investments that use the term 'series_'
inv_venture = inv_nuts2[[x for x in inv_nuts2.columns if 'series_' in x]].sum(axis=1)

inv_venture.name = 'venture_capital_investment'

inv_venture = pd.DataFrame(inv_venture)

#Extract indicator
out = make_indicator(inv_venture,
                     {'venture_capital_investment':'gbp_venture_capital_received'},
              year_var='year',nuts_spec='flex',nuts_var='nuts_code',decimals=0)

save_indicator(out,'crunchbase','gbp_venture_capital_received')
