#Utilities to manage directories and files including saves, creation of schemas etc.

import os
import pandas as pd
import re
import beis_indicators
import numpy as np
import logging

from beis_indicators.utils.nuts_utils import *

project_dir = beis_indicators.project_dir

def make_dirs(name, dirs=['raw', 'processed']):
    '''
    Utility that creates directories to save the data

    '''
    for d in dirs:
        if name not in os.listdir(f'{project_dir}/data/{d}'):
            os.mkdir(f'{project_dir}/data/{d}/{name}')

def tidy_cols(my_csv):
    '''
    Tidies column names ie lower and replace spaces with underscores

    '''
    return([re.sub(' ', '_', col.lower()) for col in my_csv.columns])

def get_nuts_category(year):
    '''
    Function that returns the nuts2 year in place for a year
    '''
    if year >= 2016:
        return(f'nuts2_2016')
    elif year >=2013:
        return(f'nuts2_2013')
    elif year >= 2010:
        return(f'nuts2_2010')
    elif year >= 2006:
        return(f'nuts2_2006')
    else:
        return(f'nuts2_2003')



    # for t in [2016,2013,2010,2006,2003]:
    #     if year >=t:
    #         return(f'nuts2_{str(t)}')

def get_nuts_spec(year):
    '''
    Function that returns the nuts2 year in place for a year
    '''
    for t in [2016, 2013, 2010, 2006, 2003]:
        if year >=t:
            return(t)

def parse_academic_year(year):
    '''
    Parses an academic year eg 2014/15 into an int with the first year

    '''
    return(int(year.split('/')[0]))

def make_indicator(table, var_lookup, year_var, nuts_var='nuts_code', nuts_spec='flex', decimals=0):
    '''
    We use this function to create indicators using our standardised format.

    Args:
        table (df) is a df with relevant information
        var_lookup (dict) is a lookup to rename the variable into our standardised name
        year (str) is the name of the year variable
        geo_var (str) is the name of the NUTS or LEP code variable. We assume it is nuts_code
        geo_spec (str) is the method to set up the nuts or lep specification. If flex, this means that we adapt it to the year.
        if not flex then it is the year we specify as a value.
        decimals (int) number of decimals (0 if an int)

    '''
    #Copy
    t = table.reset_index(drop=False)

    #Reset index (we assume that the index is the nuts code, var name and year - this might need to be changed)
    #Process the interim data into an indicator

    #This is the variable name and code
    var_name = list(var_lookup.keys())[0]

    var_code = list(var_lookup.values())[0]

    #Focus on those
    t = t[[year_var, nuts_var, var_name]]

    #Add the nuts specification
    if geo_type == 'nuts':
        if geo_spec=='flex':
            t['nuts_year_spec'] = [get_nuts_spec(x) for x in t[year_var]]
            #Rename variables
            t.rename(columns={var_name:var_code,year_var:'year',nuts_var:'nuts_id'},inplace=True)
            #Round variables
            t[var_code] = [np.round(x,decimals) if decimals>0 else int(x) for x in t[var_code]]
            #Reorder variables
            t = t[['year','nuts_id','nuts_year_spec',var_code]]
        else:
            t['nuts_year_spec'] = geo_spec
            #Rename variables
            t.rename(columns={var_name:var_code,year_var:'year',nuts_var:'nuts_id'},inplace=True)
            #Round variables
            t[var_code] = [np.round(x,decimals) if decimals>0 else int(x) for x in t[var_code]]
            #Reorder variables
            t = t[['year','nuts_id','nuts_year_spec',var_code]]
    else:
        t['nuts_year_spec'] = nuts_spec

    #Rename variables
    t.rename(columns={
        var_name: var_code,
        year_var: 'year',
        nuts_var: 'nuts_id'}, inplace=True)

    #Round variables (and warn if there are missing values)
    round_results = []

    for x in t[var_code]:
        if pd.isnull(x)==True:
            round_results.append(np.nan)
        elif decimals > 0:
            round_results.append(np.round(x,decimals))
        else:
            round_results.append(int(x))

    if np.nan in round_results:
        logging.info(
        f"There are {sum([pd.isnull(x) for x in round_results])} missing values")

    t[var_code] = round_results

#    t[var_code] = [np.round(x,decimals) if decimals>0 else int(x) for x in t[var_code]]

    # #If we are dealing with academic years then we need to parse them
    # if year =='academic_year':
    #     t[year]=[parse_academic_year(y) for y in t[year]]

    #Reorder variables
    t = t[['year', 'nuts_id', 'nuts_year_spec', var_code]]

    print(t.head())

    return(t)

def save_indicator(table, target_path, var_name):
    '''
    Function to save an indicator

    Args:
        table (pandas.DataFrame)
        path (str)
        var_name (variable name)

    '''
    table.to_csv(f'{target_path}/{var_name}.csv',index=False)
