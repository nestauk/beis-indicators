#Utilities to manage directories and files including saves, creation of schemas etc.

import os
import pandas as pd 
import re
import beis_indicators

project_dir = beis_indicators.project_dir

def make_dirs(name,dirs = ['raw','processed']):
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
    
    return([re.sub(' ','_',col.lower()) for col in my_csv.columns])


def get_nuts_category(year):
    '''
    Function that returns the nuts2 year in place for a year
    '''
    for t in [2016,2013,2010,2006,2003]:
        if year >=t:
            return(f'nuts2_{str(t)}')

def get_nuts_spec(year):
    '''
    Function that returns the nuts2 year in place for a year
    '''
    for t in [2016,2013,2010,2006,2003]:
        if year >=t:
            return(t)

def make_indicator(table,target_path,var_lookup,year_var,nuts_var='nuts_code',nuts_spec='flex'):
    '''
    We use this function to create and save indicators using our standardised format.
    
    Args:
        table (df) is a df with relevant information
        target_path (str) is the location of the directory where we want to save the data (includes interim and processed)
        var_lookup (dict) is a lookup to rename the variable into our standardised name
        year (str) is the name of the year variable
        nuts_var (str) is the name of the NUTS code variable. We assume it is nuts_code
        nuts_spec (str) is the method to set up the nuts specification. If flex, this means that we adapt it to the year.
        if not flex then it is the year we specify as a value.
    
    '''
    #Copy
    t = table.reset_index(drop=False)
    
    #Reset index (we assume that the index is the nuts code, var name and year - this might need to be changed)
    
    
    #Process the interim data into an indicator
    
    #This is the variable name and code
    var_name = list(var_lookup.keys())[0]
    
    var_code = list(var_lookup.values())[0]
    
    #Focus on those
    t = t[[year_var,nuts_var,var_name]]
    
    #Add the nuts specification
    if nuts_spec=='flex':
        t['nuts_year_spec'] = [get_nuts_spec(x) for x in t[year_var]]
    else:
        t['nuts_year_spec'] = nuts_spec
    
    #Rename variables
    t.rename(columns={var_name:var_code,year_var:'year',nuts_var:'nuts_id'},inplace=True)

    
    #Reorder variables
    t = t[['year','nuts_id','nuts_year_spec',var_code]]
    
    print(t.head())
    
    #Save in the processed folder
    t.to_csv(f'{project_dir}/data/processed/{target_path}/{var_code}.csv')
    
    