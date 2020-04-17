#Script to make HESA indicators

import csv
import io
import json
import numpy as np
import os
import random
import requests
import zipfile

from ast import literal_eval

from data_getters.labs.core import download_file

import beis_indicators
from beis_indicators.utils.dir_file_management import *
project_dir = beis_indicators.project_dir

#Make directories
make_dirs('patents',['raw','processed','interim'])
                        
def flatten_list(a_list):
    
    return([x for el in a_list for x in el])   

#Download data from nesta data getters
def patent_download(file_path=None, progress=True):
    '''
    Fetch patent data

    Repo: http://github.com/nestauk/patent_analysis
    Commit: cb11b3f
    File: https://github.com/nestauk/patent_analysis/blob/master/notebooks/02-jmg-patent_merge.ipynb

    Args:
        file_path (`str`, optional): Path to download to. If None, stream file.
        progress (`bool`, optional): If `True` and `file_path` is not `None`,
            display download progress.
    '''
    item_name = "Scotland_temp/15_10_2019_patents_combined.csv"
    return download_file(item_name, file_path, progress)


def count_patenting_in_nuts(df,variable,nuts_lookup,pat_fam_id='docdb_family_id'):
    '''
    This function creates counts of inventors and applicants in NUTS areas.
    
    Note that the NUTS areas are not available at an standardised level of resolution. 
        We will prune the length of NUTS3 (length of code>4) and match with the 
        nuts2 code lookup. 

    This also means we will throw away any patents that don't have better 
    level of resolution than NUTS2.
    
    Args:
        df (dataframe) is the df with the patent information. Each row is a 
            patent id and the columns contain metadata, authorship etc.
        variable (str) is the variable we want to use in the analysis
        pat_fam_id (str) is the patent family variable that we want to focus on
        nuts_lookup (dict) is the nuts2 code to name lookup
    
    '''
    
    #Group by patent families
    
    #This gives us a set of nuts regions involved in a single invention. 
    #Note that this is binary (whether a nuts region participates in an invention, 
    #rather than the number of participants)
    #That would require a different approach using a person - patent lookup
    
    #All this drama is because we are concatenating lists, so we need to flatten them first
    # This gives us the NUTS involved in a patent family

    fam = df.dropna(subset=[variable]).groupby(pat_fam_id)[variable].apply(
                                                    lambda x: list(set(flatten_list(list(x))))
                                                    ).reset_index(drop=False)
    #We need the earliest application year for every patent id
    fam_year_lookup = df.drop_duplicates(pat_fam_id).set_index(
                                                    pat_fam_id)['earliest_publn_year'].to_dict()

    #This adds a year field to the fam df
    fam['earliest_publn_year'] = [fam_year_lookup[x] for x in fam[pat_fam_id]]

    #In Fam, we have in some cases multiple NUTS per application. We extract them using the unfold field variable
    #We also concatenate them
    fam_unfolded = pd.concat([unfold_field(x,variable,
                            'earliest_publn_year') for item,x in fam.iterrows()])
    
    #We extract the nuts 2 using nuts lookup. Note that there will be some missing values (eg the 'UK') value
    fam_unfolded['nuts_2'] = [nuts_lookup[x] if x in nuts_lookup.keys(
                                        ) else np.nan for x in fam_unfolded[variable]]

    #Crosstab to obtain the counts of NUTS2 per year
    patent_year_counts = pd.crosstab(fam_unfolded['nuts_2'],
                                     fam_unfolded['earliest_publn_year']).reset_index(
                                     drop=False)

    #And melt
    patent_year_counts_long = patent_year_counts.melt(
                                    id_vars='nuts_2').set_index(
                                    ['nuts_2','earliest_publn_year'])
    
    patent_year_counts_long.rename(columns={'value':variable+'_n'},inplace=True)
    
    return patent_year_counts_long

def unfold_field(pat_item,variable,year_var):
    '''
    Some of the family patents involve multiple NUTS. 
    We need to extract those so that we have one NUTS to year.
    
    Args:
        pat_item (df item) is an item with a list of nuts involved in a patent 
            family and the earliest year when it was files
        variable (str) is the name of the variable (could be inventor nuts) 
        year_var (str) is the name of the year variable
    
    '''   
    nuts = []
    years = []
    
    for n in pat_item[variable]:
        nuts.append(n)
        years.append(pat_item[year_var])

    out = pd.DataFrame({variable:nuts,year_var:years})

    return out

########
#0. Metadata
#########

nuts = pd.read_csv('https://opendata.arcgis.com/datasets/d266cbe2179a4766b4de7c6e73b4a285_0.csv')

#This is a NUTS 2 lookup FOR 2015 (ie 2013 in EU terms)
nuts_2_code_name_lookup = nuts.drop_duplicates('NUTS215CD').set_index(
                                                'NUTS215CD')['NUTS215NM'].to_dict()

#nuts_2_code_name_lookup = nuts.drop_duplicates('NUTS218CD').set_index('NUTS218CD')['NUTS218NM'].to_dict()

#We create a lookup between NUTS2 and NUTS3 codes
nuts_3_to_2 = nuts.set_index('NUTS315CD')['NUTS215CD'].to_dict()

#This is a NUTS code - lookup name for all NUTS codes regardless of their level
with open(f'{project_dir}/data/aux/patstat_nuts_lookup.json','r') as infile:
    nuts_patstat_lookup = json.load(infile)

########
#1. Collect data
########
p_d = patent_download()

p = pd.read_csv(p_d)

#Convert some strings into lists, remove missing values from inside the lists
for v in ['inv_nuts','appl_nuts']:
    p[v] = [literal_eval(x) if pd.isnull(x)==False else np.nan for x in p[v]]

    p[v] = [[x for x in el if pd.isnull(x)!=np.nan] if type(el)==list else np.nan for el in p[v]]

#########
#2. Process data & make indicators
##########

#Create count of applications and inventions per NUTS area and year 
#focusing on the earliest publication year. We focus on patent families to avoid double counting.

rec = p.loc[(p['earliest_publn_year']>2012)&(p['earliest_publn_year']<2019)]

pat_nuts = pd.concat(
    [count_patenting_in_nuts(rec,var,nuts_3_to_2) 
     for var in ['inv_nuts','appl_nuts']],axis=1).fillna(0)

ind = make_indicator(
                     pat_nuts,{'inv_nuts_n':'total_inventions'},
                     'earliest_publn_year',nuts_var='nuts_2',nuts_spec='flex')

save_indicator(ind,f'{project_dir}/data/processed/patents','total_inventions')