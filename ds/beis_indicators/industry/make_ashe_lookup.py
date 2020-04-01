## Logging
import logging
import sys
import requests
from zipfile import ZipFile
from io import BytesIO

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
from beis_indicators.utils import dir_file_management

project_dir = beis_indicators.project_dir

def get_ashe_data(path,ons_path):
    '''
    Function to collect the ASHE data from the ONS website.
    
    Arguments:
        path (str) is the path for the file we are interested in
        ons_path (str) is the parent for all ashe files
        
    This will return a doanloaded and parsed file
    
    '''
    
    file = requests.get(ons_path+path)
    
    #Create a zipfile with its content
    z = ZipFile(BytesIO(file.content))
    
    #Extract names
    names = z.namelist()
    
    #Select the names (they will meantion hourly gross but not the confidence intervals)
    
    my_name = [x for x in names if (all(names in x for names in ['Annual','Gross'])) & ('CV' not in x)]
    
    print(my_name)

    #if len(my_name)>1:
    #    print('Too many options')
    #    break
    
    #Read into excel
    infile = pd.read_excel(BytesIO(z.open(my_name[0]).read()),sheet_name=1,skiprows=4,
                      na_values=['x','..',':'])
    
    #Drop missing values in the matching code or median (these don't interest us)
    infile.dropna(axis=0,subset=['Code'],inplace=True)
    
    infile['Code'] = [x.strip() for x in infile['Code']]
    
    #container.append(infile.reset_index(drop=True))
    
    return(infile.reset_index(drop=True))

#Processing files
def add_zeros(container):
    '''
    This adds pre-zeroes to codes in categories A and B
    
    Args:
        Container (df) is one of the dataframes we have created before
    
    ''' 
    new_cont = container.copy()
    
    for pid,row in new_cont.iterrows():
        
        if row['Code']=='C':
            break
        else:
            if row['Code'] not in ['A','B']:
            
            #print(row['Code'])
                new_cont.loc[pid,'Code']='0'+row['Code']
        
    return(new_cont)
    
def year_ashe_lookups(ashe_table):
    '''
    
    Takes an ashe table and outputs a list of code lookups depending on the level of resolution at which they are available
    
    Args:
        ashe_table: an ashe table as above
        
    returns three dicts with code - salary lookups with decreasing levels of resolution
    
    '''
    #Containers
    ashe_4 = {}
    ashe_3 = {}
    ashe_2 = {}

    #In each row it gets the length of a code (sic4,3 etc) and assigns the median salary to the right dict.
    #We we will use this later to assign the median to 
    
    for pid, row in ashe_table.iterrows():

        code = row['Code'].strip()
        med_sal = row['Median']

        if len(code)==4:
            ashe_4[code]= med_sal

        elif len(code)==3:
            ashe_3[code] = med_sal

        elif len(code)==2:
            ashe_2[code] = med_sal

        else:
            pass
        
    return([ashe_4,ashe_3,ashe_2])
    
def map_salaries(lookup,four_digit, ashe):
    '''
    
    Assigns each 4-digit sic code a median according to ASHE at its finest level of resolution
    
    Args:
        lookup (df) a lookup with the 4 digit sic code we want to query against our ashe lookups
        four_digit (str) the name of the variable with the four digits
        ashe_lookups (list of dicts) the list of ashe code-median key-value pairs to query
        
    Returns
        a table with four digit sics, names and salaries.
    
    
    ''' 
    cont = []

    #Is loo
    for sic in lookup[four_digit]:
        
        if sic in ashe[0].keys():
            #cont.append({sic:ashe_lookups[0][sic]})
            cont.append([sic,ashe[0][sic]])
            
        elif sic[:-1] in ashe[1].keys():
            
            #cont.append({sic:ashe_lookups[1][sic[:-1]]})
            cont.append([sic,ashe[1][sic[:-1]]])
        
        elif sic[:-2] in ashe[2].keys():
            #cont.append({sic:ashe_lookups[2][sic[:-2]]})
            cont.append([sic,ashe[2][sic[:-2]]])
        
        else:
            #cont.append({sic:np.nan})
            cont.append([sic,np.nan])
    
    return(pd.DataFrame(cont,columns=['sic_4','median_salary_thGBP']).set_index('sic_4'))
        

##########
#1. Collect data
##########
    
standard_path = 'https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/industry4digitsic2007ashetable16/'

#Ashe paths
ashe_paths = ['2018provisional/table162018provisional.zip', '2017revised/table162017revised.zip',
            '2016revised/table162016revised.zip','2015/table162015revised.zip']

#Collect data
ashes = [get_ashe_data(p,standard_path) for p in ashe_paths]

#Add zeroes at the beginning of some categories
new_containers = [add_zeros(x) for x in ashes]

#Red the segment lookup
cl = pd.read_csv(f'{project_dir}/data/raw/sic_4_industry_segment_lookup.csv',dtype={'sic_4':str})

#############
#2. Process data
##############

#Create 2 digit and 4 digit lookups from ASHE
all_ashe_lookups = [year_ashe_lookups(cont) for cont in new_containers]
all_salaries = pd.concat([map_salaries(cl,'sic_4',tab) for tab in all_ashe_lookups],axis=1)
all_salaries.columns = [2018,2017,2016,2015]

#Create weighted medians
#Melt the salaries file
salaries_long = all_salaries.reset_index(drop=False).melt(id_vars=['sic_4'],var_name='year',value_name='median_salary')

#REad BRES data for the four years
#We read for the four years
bres_data = pd.concat([pd.read_csv(f'{project_dir}/data/interim/industry/nomis_BRES_{y}_TYPE450.csv',
                                   dtype={'SIC4':str}) for y in [2016,2017,2018]],axis=0)

#Group them by year to get the total level of employment by SIC4
sic_yearly_long = bres_data.groupby(['year','SIC4'])['value'].sum().reset_index(drop=False)

sic_yearly_long.rename(columns={'value':'employment'},inplace=True)

salary_empl_merge = pd.merge(salaries_long,sic_yearly_long,left_on=['sic_4','year'],right_on=['SIC4','year'])

segment_merged = pd.merge(cl[['sic_4','cluster']],salary_empl_merge,left_on='sic_4',right_on='sic_4')

#Weighted salary: takes all the sics in a segment and applies a weight based on their importance in the segment
weighted_sal = segment_merged.groupby(
    ['cluster','year']).apply(lambda x: np.sum(x['median_salary']*x['employment'])/np.sum(x['employment'])).reset_index(
    drop=False)

ashe_out = weighted_sal.rename(columns={0:'weighted_median_salary'})

ashe_out.pivot_table(index='cluster',columns='year',values='weighted_median_salary').corr()

#Remove some outliers
for pid,row in ashe_out.iterrows():
    
    if row['weighted_median_salary']<1000:
    
        ashe_out.loc[pid,'weighted_median_salary'] = np.nan

#Calculate averages for all years
ashe_out_grouped = pd.DataFrame(ashe_out.groupby(['cluster'])['weighted_median_salary'].mean())

ashe_out_grouped['ashe_median_salary_rank'] = pd.qcut(ashe_out_grouped['weighted_median_salary'],np.arange(0,1.1,0.1),
                                                      labels=False)

#ashe_out_grouped.sort_values('ashe_median_salary_rank',ascending=False).tail()

ashe_out_grouped.to_csv(f'{project_dir}/data/interim/industry/ashe_rankings.csv')

