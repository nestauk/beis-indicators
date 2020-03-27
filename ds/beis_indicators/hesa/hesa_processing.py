#Script to make HESA indicators

import csv
import zipfile
import io
import os
import requests
import beis_indicators
import numpy as np
import json

from beis_indicators.utils.dir_file_management import *

project_dir = beis_indicators.project_dir


def filter_data(data,var_val_pairs):
    '''
    We use this to filter the data more easily than using pandas subsetting
    
    Args:
        data (df) is a dataframe
        var_val pairs (dict) is a dictionary where the keys are variables and the value are values

    
    '''
    d = data.copy()
    
    for k,v in var_val_pairs.items():
        d = d.loc[d[k]==v]
        
    return(d.reset_index(drop=True))
    

def hesa_parser(url,out_name,skip=16,encoding='utf-8'):
    '''
    Function to obtain and parse data from the HESA website 
    
    Args:
        url (str) is the location of the csv file
        out_name (str) is the saved name of the file
        skip is the number of rows to skip (we could automate this by looking for rows at the top with lots of nans)
    
    '''

    if f'{out_name}.txt' not in os.listdir(f'{project_dir}/data/raw/hesa/'):

        
        #Request and parse
        rs = requests.get(url)
        
        #Parse the file
        parsed = rs.content.decode(encoding)
        
        #Save it
        
        with open(f'{project_dir}/data/raw/hesa/{out_name}.txt','w') as outfile:
            outfile.write(parsed)
            
        #Read it.
        my_csv = pd.read_csv(f'{project_dir}/data/raw/hesa/{out_name}.txt',skiprows=skip)
        
        #Clean column names
        my_csv.columns = tidy_cols(my_csv)
        
        
        return(my_csv)

    else:
        print(f'Already collected {out_name}')
        out = pd.read_csv(f'{project_dir}/data/raw/hesa/{out_name}.txt',skiprows=skip,dtype={'UKPRN':str})

        out.columns = tidy_cols(out)

        #Turn the academic year into int year
        out['academic_year'] = [parse_academic_year(x) for x in out['academic_year']]

        return(out)


def parse_academic_year(year):
    '''
    Parses an academic year eg 2014/15 into an int with the first year

    '''

    return(int(year.split('/')[0]))




def make_nuts_estimate(data,nuts_lookup,counter,name,year_var=None,method='time_consistent'):
    '''
    This function takes hesa data and creates a nuts estimate
    
    Args:
        data (df) where we have already selected variables of interest eg mode of employment
        nuts (dict) is the ukprn - nuts name and code lookup
        counter (str) is the variable with counts that we are interested in
        year_var (str) is the variable containing the years we want to group by. If None, then we are not grouping by year
        method (str) is whether we are creating the indicator using a time consistent approach (each year in its NUTS category) or using the latest nuts
    
    '''
    
    d = data.copy()
    
    #Add the nuts names and codes

    #If time consistent...
    if method == 'time_consistent':
        d['nuts_code'] = [nuts_lookup[row['ukprn']][get_nuts_category(row['academic_year'])] if row['ukprn'] in nuts_lookup.keys() else np.nan for rid,row in data.iterrows()]
    else:
        d['nuts_code'] = [nuts_lookup[row['ukprn']]['nuts2_2016'] if row['ukprn'] in nuts_lookup.keys() else np.nan for rid,row in data.iterrows()]


    #We are focusing on numbers
    d[counter] = d[counter].astype(float)
    
    #Group results by year?
    if year_var == None:
        out = d.groupby('nuts_code')[counter].sum()
        
    else:
        
        out = d.groupby(['nuts_code',year_var])[counter].sum()
        
    
    out.name = name
    
    return(out)

def multiple_nuts_estimates(data,nuts_lookup,variables,select_var,value,year_var=None):
    '''
    Creates NUTS estimates for multiple variables.
    
    Args:
        data (df) is the filtered dataframe
        select_var (str) is the variable we want to use to select values
        nuts_lookup (dict) is the lookup between universities and nuts
        variables (list) is the list of variables for which we want to generate the analysis
        value (str) is the field that contains the numerical value we want to aggregate in the dataframe
        year_var (str) is the year_variable. If none, then we are not interested in years
    
    '''
    
    if year_var==None:
        concat = pd.concat([make_nuts_estimate(data.loc[data[select_var]==m],nuts_lookup,value,m) for m in 
                  variables],axis=1)
    
    #If we want to do this by year then we will create aggregates by nuts name and code and year and then concatenate over columns 
    else:
        
        year_store = []
        
        for m in variables:
            
            y = make_nuts_estimate(data.loc[data[select_var]==m],nuts_lookup,value,m,year_var='academic_year')
            
            year_store.append(y)
            
        concat = pd.concat(year_store,axis=1)
                
    return(concat)

def make_student_table(url):
    '''

    Function to create the student table

    Args:
        url (str) is the url with the zipfile for the student table

    '''

    if 'students' in os.listdir(f'{project_dir}/data/raw/hesa/'):
        print('Already collected students table')

    else:
        #Request
        rs = requests.get(url)

        #Unzip and save the file
        #Note that the file contains tables for various years. We keep all of them
        years = ['2014-15','2015-16','2016-17','2017-18','2018-19']

        out_files = [zipfile.ZipFile(io.BytesIO(rs.content)).extract(f'table-13-({year}).csv',f'{project_dir}/data/raw/hesa/students/') for year in years]

        #We use a pipe to assign a year to each df and concatenate into a single df

        graduates_all_years = pd.concat(
            [pd.read_csv(out_files[n],skiprows=14,dtype={'UKPRN':str}) for n in np.arange(len(out_files))],axis=0)

        graduates_all_years.columns = tidy_cols(graduates_all_years)

        graduates_all_years['academic_year'] = [parse_academic_year(x) for x in graduates_all_years['academic_year']]

        graduates_all_years.to_csv(f'{project_dir}/data/raw/hesa/students.csv',index=False)

        print('parsed collected and parsed students')
        