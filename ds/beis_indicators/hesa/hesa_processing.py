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
from beis_indicators.utils.geo_utils import leps_year_spec
from beis_indicators.utils.nuts_utils import nuts_earliest

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
        
    return d.reset_index(drop=True)
    
def hesa_parser(url, out_name, skip=16, encoding='utf-8'):
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
        
        return my_csv

    else:
        print(f'Already collected {out_name}')
        out = pd.read_csv(f'{project_dir}/data/raw/hesa/{out_name}.txt',skiprows=skip,dtype={'UKPRN':str})

        out.columns = tidy_cols(out)

        #Turn the academic year into int year
        out['academic_year'] = [parse_academic_year(x) for x in out['academic_year']]

        return out

def university_indicator(data, geo_data, region_type, value_header, value='number', category=None, category_col=None):
    """university_indicator

    Args:
        data (pd.DataFrame):
        geo_data (pd.DataFrame):
        variable (str):
        select_variable (str):
        value_name (str):
    
    Returns:
        
    """
    if category is not None:
        data = data[data[category_col] == category]

    geo_data['ukprn'] = pd.to_numeric(geo_data['ukprn'])
    data['ukprn'] = pd.to_numeric(data['ukprn'], errors='coerce')
    data[value] = data[value].astype('float')
    data = data.dropna(subset=['ukprn'])

    if 'nuts' in region_type:
        year_col = 'nuts_year_spec'
        region_id_col = 'nuts_id'
        groupby_year_col = 'nuts_year_spec'
        data['year_regions'] = data['academic_year'].apply(nuts_earliest)
    elif region_type == 'lep':
        year_col = 'lep_year_spec'
        groupby_year_col = 'lep_year_spec'
        region_id_col = 'lep_id'
        data['year_regions'] = data['academic_year'].apply(leps_year_spec)
    
    df = pd.merge(data, geo_data, left_on=['year_regions', 'ukprn'], 
            right_on=[year_col, 'ukprn'])
    df = df.groupby(['academic_year', region_id_col, groupby_year_col], as_index=False)[value].sum()

    df = df.rename(columns={value: value_header, 'academic_year': 'year'})
    df = df [['year', region_id_col, groupby_year_col, value_header]]
    df = df.sort_values(by=[region_id_col, 'year'])
    return df

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

def calculate_perf(table,perf,nuts_lookup,norm=False,sp_def='all',value='currency',method='time-consistent'):
    '''
    Function that calculates performance with HEBCI data (employment, turnover, investment, active firms...) 
    
    Args:
        table (df) long table with the performance and spinoff category information
        #nuts_lookup (dict) is the lookup we use for the nuts.
        perf (str) measure of performance
        sp_def (str) definition of spinoff
        norm (str) if we want to normalise by the number of entities in the category
        value (str) if currency multiply by 1000 to extract gpbs
        method (str) whether we are reverse geocodign variables in a time-consistent way
    
    Returns a clean indicator
    
    '''
    t = table.copy()
    
    #First get the financials
    #Create a dict to filter the data
    p_filter = {'metric':perf}
    
    #Extract the estimates
    t_filt= multiple_nuts_estimates(filter_data(t,p_filter),nuts_lookup,set(table['category_marker']),
                                    'category_marker','value',year_var='academic_year',method=method)
    

    #Are we subsetting by a category?
    if sp_def == 'all':
        t_filt = t_filt.sum(axis=1)
    
    else:
        t_filt = t_filt[sp_def]
    
    #Tidy columns
    t_filt.name = sp_def

    #Scale if the value is a currency
    if value=='currency':
        t_filt = t_filt*1000
        t_filt.name = 'gbp_'+t_filt.name
    
    #Do the same with the totals
    if norm == True:
        
        unit_filter = {'metric':'Number of active firms'}
        
        u_filt= multiple_nuts_estimates(filter_data(t,unit_filter),nuts_lookup,set(table['category_marker']),
                                        'category_marker','value',year_var='academic_year',method=method)
        
        #Are we subsetting by a category?
        if sp_def == 'all':
            u_filt = u_filt.sum(axis=1)

        else:
            u_filt = u_filt[sp_def]

        #Tidy columns
        u_filt.name = 'all_comps'
        
        comb = pd.concat([t_filt,u_filt],axis=1)
        
        comb[f'{t_filt.name}_by_company']= comb[t_filt.name]/comb['all_comps']
        
        #Zeroes are nans (this is to avoid division by zero)
        comb.fillna(0,inplace=True)
        
        return(comb)
    
    else:
        return(t_filt)
        
