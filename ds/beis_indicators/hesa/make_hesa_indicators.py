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
make_dirs('hesa',['raw','processed','interim'])

#Read the uni-nuts lookup
with open(f'{project_dir}/data/interim/uni_geos.json','r') as infile:
    uni_nuts = json.load(infile)

#We load a STEM discipline list
with open(f'{project_dir}/data/aux/stem_hesa.txt','r') as infile:
    
    stem_hesa = infile.read().split('\n')

#Collect data if necessary
#Staff

res_staff = hesa_parser('https://www.hesa.ac.uk/data-and-analysis/staff/table-1.csv','staff',skip=28)

#Staff qualifications
qual_staff = hesa_parser('https://www.hesa.ac.uk/data-and-analysis/staff/table-8.csv','qual_staff',skip=18)

#Spaces
spaces = hesa_parser('https://www.hesa.ac.uk/data-and-analysis/estates/data.csv','spaces',11)

#STEM graduates
#This is a larger file so we use a different approach
make_student_table('https://www.hesa.ac.uk/data-and-analysis/students/table-13.csv')

graduates_all_years = pd.read_csv(f'{project_dir}/data/raw/hesa/students.csv',dtype={'ukprn':str})


########
#Process the data
#######

#We filter the graduate data to focus on the full-time students. 
grad_short = graduates_all_years.loc[(graduates_all_years['level_of_study']=='All')&((graduates_all_years['mode_of_study']=='Full-time'))]


###########
#Produce indicators
###########

#Research staff

res_staff_filter = {'mode_of_employment':'All','contract_marker':'Academic',
                   'activity_standard_occupational_classification':'Total academic staff',
                   'country_of_he_provider':'All','region_of_he_provider':'All'}

res_filtered = filter_data(res_staff,res_staff_filter)

nuts_academics = make_nuts_estimate(res_filtered,uni_nuts,'number','academic_staff','academic_year')

#Research space
space_vars = ['Research income (£)','Research student FTE','Total number of buildings','Total site area (hectares)']

nuts_spaces = multiple_nuts_estimates(spaces,uni_nuts,space_vars,'category_marker','value',year_var='academic_year')

#Number of STEM graduates
grad_filter = {'country_of_he_provider':'All','region_of_he_provider':'All'}

grad_filtered = filter_data(grad_short,grad_filter)

disciplines = set(grad_filtered['subject_of_study'])

nuts_disciplines = multiple_nuts_estimates(grad_filtered,uni_nuts,disciplines,'subject_of_study','number',year_var='academic_year')

#Number of postgraduates
#We will filter the data to focus on full time postgraduate researchers
post_grad_filter = grad_filter.copy()

post_grad_filter['level_of_study'] = 'Postgraduate (research)'
post_grad_filter['mode_of_study'] = 'Full-time'
post_grad_filter['subject_of_study_marker']= 'Subject area'

post_grad_filtered = filter_data(graduates_all_years,post_grad_filter)

nuts_postgrads = make_nuts_estimate(post_grad_filtered,uni_nuts,'number','postgrad_research',year_var='academic_year')

#STEM postgraduates
post_grad_filter = {'country_of_he_provider':'All','region_of_he_provider':'All','mode_of_study':'Full-time','level_of_study':'Postgraduate (research)',
                   'subject_of_study_marker':'Subject area'}

postgrad_filtered = filter_data(grad_short,post_grad_filter)

#Extract information
nuts_postgrad_discipline = multiple_nuts_estimates(post_grad_filtered,uni_nuts,disciplines,'subject_of_study','number',year_var='academic_year')

#Stem students
stem_students = nuts_disciplines[stem_hesa].sum(axis=1)

stem_students.name = 'stem_students'

#Extract STEM subjects
stem_postgrads_detailed = nuts_postgrad_discipline[stem_hesa]

#Aggregate them
stem_postgraduates = stem_postgrads_detailed.sum(axis=1)

stem_postgraduates.name = 'stem_postgraduate_students'

################
#Output indicators
################

#FTE res students
make_indicator(nuts_spaces,'hesa',{'Research student FTE':'fte_research_students'},'academic_year')

#Research income
make_indicator(nuts_spaces,'hesa',{'Research income (£)':'gbp_research_income'},'academic_year')

#Students in STEM disciplines
make_indicator(stem_students,'hesa',{'stem_students':'total_stem_students'},'academic_year')

#STEM postgraduates
make_indicator(stem_postgraduates,'hesa',{'stem_postgraduate_students':'total_stem_postgraduates'},'academic_year')

#Site areas
make_indicator(nuts_spaces,'hesa',{'Total site area (hectares)':'area_university_site'},'academic_year')

#Number of buildings
make_indicator(nuts_spaces,'hesa',{'Total number of buildings':'total_university_buildings'},'academic_year')




