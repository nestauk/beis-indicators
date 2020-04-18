# Import our repo as a module
import beis_indicators
from beis_indicators.utils.dir_file_management import *
from beis_indicators.geo.reverse_geocoder import *
from beis_indicators.hesa.hesa_processing import *

## Logging
import logging
import sys

## Basic data processing
import numpy as np
import pandas as pd
import re
import datetime
from ast import literal_eval

logger = logging.getLogger()

## Paths
# project directory e.g. `/home/user/GIT/nesta`
project_dir = beis_indicators.project_dir
data_path = f'{project_dir}/data'
target_path = os.path.join(data_path,'processed','ref')

#Make directory (if needed)
make_dirs('ref')

#Load NUTS json
with open(f"{project_dir}/data/interim/uni_geos.json",'r') as infile:
    unis_geos = json.load(infile)

#Load STEM discipline names
with open(f'{project_dir}/data/aux/stem_ref.txt','r') as infile:
    stem = infile.read().split('\n')

########
#1. COLLECT DATA
########

#Read HEFCE data
REF_URL = 'https://results.ref.ac.uk/(S(hlvnuqzwkag44jp3df3d4q14))/DownloadFile/AllResults/xlsx'

ref = pd.read_excel(REF_URL,skiprows=7,na_values='-')
ref.columns = [re.sub(' ','_',col.lower()) for col in ref.columns]

#Focus on variables of interest
focus_vars = ['institution_code_(ukprn)','institution_name',
'unit_of_assessment_name','profile',
'fte_category_a_staff_submitted',
'4*','3*','2*','1*','unclassified']

ref_2 = ref[focus_vars]

########
#2. PROCESS DATA
########

#Create the full time estimate equivalents in each category
for x in ['4*','3*','2*','1*','unclassified']:

    ref_2[x+'_fte'] = [fte*star/100 for fte,star in zip(ref_2['fte_category_a_staff_submitted'],
                                                        ref_2[x])]

#Focus on the overall variable rather than its components
ref_3 = ref_2.loc[ref['profile']=='Overall']

#Create tidy dataset
focus_vars_2 = ['institution_code_(ukprn)','institution_name',
'unit_of_assessment_name',
'4*_fte','3*_fte','2*_fte','1*_fte','unclassified_fte']

ref_long = ref_3[focus_vars_2].melt(id_vars=['institution_code_(ukprn)',
                                    'institution_name','unit_of_assessment_name'])

#We rename the variable with the ukprn code so it works with our functions
ref_long.rename(columns={'institution_code_(ukprn)':'ukprn'},
                inplace=True)

#We remove the institute of zoology, which does not have a UKPRN
ref_long = ref_long.loc[ref_long['ukprn']!='ZZZZZZZZ']

ref_long['ukprn'] = ref_long['ukprn'].astype('str')

#This is the year of the REF. We need it to assign nuts codes.
ref_long['year'] = 2014

#Calculate aggregations for each indicator
out = []

#For each unique discipline
for disc in set(ref_long['unit_of_assessment_name']):

    #Subset by that discipline
    df_in_unit = ref_long.loc[ref_long['unit_of_assessment_name']==disc]

    #Aggregate over nuts
    nuts_in_unit = multiple_nuts_estimates(df_in_unit,unis_geos,set(df_in_unit['variable']),
                                           'variable','value',
                                           year_var='year',
                                           method='time_consistent')

    #Add the discipline (unit of assessment) name so we know what everything is when we concatenate
    nuts_in_unit['unit_of_assessment_name'] = disc

    #Put in the list
    out.append(nuts_in_unit)

#Concatenate
nuts_ref_ftes = pd.concat(out,axis=0)

#FTE variables ordered
fte_vars = ['4*_fte','3*_fte','2*_fte','1*_fte','unclassified_fte']

nuts_ref_ftes = nuts_ref_ftes[['unit_of_assessment_name']+fte_vars]

nuts_ref_ftes['total_fte'] = nuts_ref_ftes[fte_vars].sum(axis=1)

#############
#Create the indicators
##############
ref_melted = pd.melt(nuts_ref_ftes.reset_index(drop=False),
                     id_vars=['nuts_code','unit_of_assessment_name','total_fte','year'])

ref_melted['score'] = [int(x.split('*')[0]) if 'unclassified' not in x else 0 for x in ref_melted['variable']]

#REF weighted scores
ref_weighted_scores = ref_melted.groupby([
                                         'nuts_code','year']).apply(
                                         lambda x: np.sum((x['value']/x['value'].sum())*x['score'])
                                         ).sort_values(ascending=False)

#REF Scores in STEM disciplines
ref_stem = ref_melted.loc[[x in stem for x in ref_melted['unit_of_assessment_name']]]

ref_stem_weighted_scores = ref_stem.groupby(
    ['nuts_code','year']).apply(
    lambda x: np.sum((x['value']/x['value'].sum())*x['score'])).sort_values(ascending=False)

#Excellent researchers submitted to REF
ref_excellent = nuts_ref_ftes.groupby(
    ['nuts_code','year'])['4*_fte'].sum().sort_values(ascending=False)

#################
#Save the indicators
#################
#We use a loop
for table,name in zip([ref_weighted_scores,ref_stem_weighted_scores,ref_excellent],
                 ['mean_ref','mean_ref_stem','total_4_fte']):

    table.name = name

    ind = make_indicator(table,{name:name},'year','nuts_code',decimals=2)

    save_indicator(ind,target_path,name)
