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
from beis_indicators.hesa.hesa_processing import *

project_dir = beis_indicators.project_dir

#Make directories
make_dirs('hesa', ['raw', 'processed', 'interim'])

#We load a STEM discipline list
with open(f'{project_dir}/data/aux/stem_hesa.txt', 'r') as infile:
    
    stem_hesa = infile.read().split('\n')

#Collect data if necessary
res_staff = hesa_parser('https://www.hesa.ac.uk/data-and-analysis/staff/table-1.csv', 'staff', skip=28)
qual_staff = hesa_parser('https://www.hesa.ac.uk/data-and-analysis/staff/table-8.csv', 'qual_staff', skip=18)
spaces = hesa_parser('https://www.hesa.ac.uk/data-and-analysis/estates/data.csv', 'spaces', 11)

#STEM graduates
#This is a larger file so we use a different approach
make_student_table('https://www.hesa.ac.uk/data-and-analysis/students/table-13.csv')

graduates_all_years = pd.read_csv(f'{project_dir}/data/raw/hesa/students.csv',
        dtype={'ukprn': str})
grad_short = graduates_all_years.loc[
    (graduates_all_years['level_of_study'] == 'All') 
    & (graduates_all_years['mode_of_study'] == 'Full-time')]

for region_type in ['nuts2', 'nuts3', 'lep']:
    uni_geos = pd.read_csv(f'{project_dir}/data/interim/hesa/uni_{region_type}_geos.csv')
    
    #University space
    space_name_lookup = {
            'Research student FTE': 'fte_research_students',
            'Research income (£)': 'gbp_research_income',
            'Total site area (hectares)': 'area_university_site',
            'Total number of buildings': 'total_university_buildings'}

    target_path = f"{project_dir}/data/processed/hesa"
    for var, name in space_name_lookup.items():
        ind = university_indicator(spaces, uni_geos, region_type, name, 'value',
                var, 'category') 
        fname =  name + f'.{region_type}'
        save_indicator(ind, target_path, fname)

    #Research staff
    res_staff_filter = {'mode_of_employment': 'All','contract_marker': 'Academic',
                       'activity_standard_occupational_classification': 'Total academic staff',
                       'country_of_he_provider': 'All', 'region_of_he_provider': 'All'}

    res_filtered = filter_data(res_staff, res_staff_filter)
    ind = university_indicator(res_filtered, uni_geos, region_type, 'academic_staff')
#     fname =  'academic_staff' + f'.{region_type}'
#     save_indicator(ind, target_path, fname)

    #STEM Graduates
    grad_filter = {'country_of_he_provider': 'All', 'region_of_he_provider': 'All'}
    grad_filtered = filter_data(grad_short, grad_filter)
    grad_stem = grad_filtered[grad_filtered['subject_of_study'].isin(stem_hesa)]
    
    ind_stem_grads = university_indicator(grad_stem, uni_geos, region_type, 
            'total_stem_students')

    fname =  'total_stem_students' + f'.{region_type}'
    save_indicator(ind_stem_grads, target_path, fname)

    #Number of postgraduates
    #We will filter the data to focus on full time postgraduate researchers
    post_grad_filter = grad_filter.copy()
    post_grad_filter['level_of_study'] = 'Postgraduate (research)'
    post_grad_filter['mode_of_study'] = 'Full-time'
    post_grad_filter['subject_of_study_marker'] = 'Subject area'

    post_grad_filtered = filter_data(graduates_all_years, post_grad_filter)
    ind_name = 'total_postgraduates'
    ind_post_grads = university_indicator(post_grad_filtered, uni_geos, region_type, 
            'total_postgraduates')
    save_indicator(ind_post_grads, target_path, ind_name + f'.{region_type}')

    #STEM postgraduates
#     import pdb; pdb.set_trace()
    post_grad_filter = {
            'country_of_he_provider': 'All',
            'region_of_he_provider': 'All',
            'mode_of_study': 'Full-time',
            'level_of_study': 'Postgraduate (research)',
            'subject_of_study_marker': 'Subject area'}

    postgrad_filtered = filter_data(graduates_all_years, post_grad_filter)
    ind_name = 'total_stem_postgraduates'
    postgrad_stem = postgrad_filtered[postgrad_filtered['subject_of_study'].isin(stem_hesa)]
    ind_postgrads_stem = university_indicator(postgrad_stem, uni_geos, region_type, 
            ind_name)
    save_indicator(ind_postgrads_stem, target_path, ind_name + f'.{region_type}')

