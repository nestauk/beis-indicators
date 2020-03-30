#Script to make HESA indicators

import csv
import zipfile
import io
import os
import requests
import beis_indicators
import numpy as np
import json
import numpy as np

from beis_indicators.utils.dir_file_management import *
from beis_indicators.hesa.hesa_processing import *

project_dir = beis_indicators.project_dir

#Make directories
make_dirs('hebci',['raw','processed','interim'])

#Read the uni-nuts lookup
with open(f'{project_dir}/data/interim/uni_geos.json','r') as infile:
    uni_nuts = json.load(infile)

################
#1. Collect data
################

#spin out activity
url_1 = 'https://www.hesa.ac.uk/data-and-analysis/providers/business-community/table-4e.csv'
spin = hesa_parser(url_1,'spin',skip=11) 

#Licensing income
url_2 = 'https://www.hesa.ac.uk/data-and-analysis/providers/business-community/table-4d.csv'
ip = hesa_parser(url_2,'ip',skip=11)

#Services income
url_3 = 'https://www.hesa.ac.uk/data-and-analysis/providers/business-community/table-2a.csv'
services = hesa_parser(url_3,'services',skip=11)

#Collaborative research involving public funding
url_4 = 'https://www.hesa.ac.uk/data-and-analysis/providers/business-community/table-1.csv'
collab = hesa_parser(url_4,'collab',skip=11)

######################
#2. Produce and output indicators
######################

#Graduate startup rate
startup_rate = calculate_perf(spin,'Number of active firms',nuts_lookup=uni_nuts,sp_def='Graduate start-ups',value='count')

make_indicator(startup_rate,'hebci',{'Graduate start-ups':'total_active_graduate_startups'},
               year_var='academic_year',decimals=0)

#Turnover per spinout
turn_per_startup = calculate_perf(spin,'Estimated current turnover of all active firms (£ thousands)',
                                  nuts_lookup=uni_nuts,norm=True,
                                  sp_def='all',value='currency')


make_indicator(turn_per_startup,'hebci',{'gbp_all_by_company':'gbp_turnover_per_active_spinoff'},
               year_var='academic_year',decimals=0)

#Average external investment per spinout
#This is the same as above but with investment instead of turnover. 
#We will focus on all companies because we have found some mistakes in the data. 
#For example, Cranfield university has recorded £500K of investment recorded vs formal spinoffs, but no active companies.

inv_per_formal = calculate_perf(spin,'Estimated external investment received (£ thousands)',norm=True,
                                nuts_lookup=uni_nuts,sp_def='all',value='currency')

make_indicator(inv_per_formal,'hebci',{'gbp_all_by_company':'gbp_investment_per_active_spinoff'},
               year_var='academic_year',decimals=0)

#Licensed income related
ip_filter = {'category_marker':'Total IP revenues'}

#Multiply by 1000 to convert into GBP
income_nuts = 1000*make_nuts_estimate(filter_data(ip,ip_filter),uni_nuts,'value','total_ip_revenues',year_var='academic_year')

make_indicator(income_nuts,'hebci',{'total_ip_revenues':'gbp_ip_revenues'},year_var='academic_year',decimals=0)

#Services related
services_filter = {'type_of_service':'Consultancy','number/value_marker':'Value'}

#Note that, as before, we are multiplying by 1000 as we are dealing with GBPs
services_nuts = 1000*multiple_nuts_estimates(filter_data(
    services,services_filter),uni_nuts,
set(services['type_of_organisation']),'type_of_organisation','number/value','academic_year')

services_nuts.columns = tidy_cols(services_nuts)

#Select consultancy with SMEs and other companies
services_nuts['business_consultancy'] = services_nuts.iloc[:,0]+services_nuts.iloc[:,2]

make_indicator(services_nuts,'hebci',
               {'business_consultancy':'gbp_business_consulting'},year_var='academic_year',decimals=0)

#Consultancy with public sector organisations
make_indicator(services_nuts,'hebci',{'non-commercial_organisations':'gbp_non_business_consulting'},
               year_var='academic_year',decimals=0)

#Contract research with business
contract_res_filter = {'type_of_service':'Contract research','number/value_marker':'Value'}

#Note that, as before, we are multiplying by 1000 as I am dealing with businesses
res_nuts = 1000*multiple_nuts_estimates(filter_data(
    services,contract_res_filter),uni_nuts,set(services['type_of_organisation']),'type_of_organisation','number/value','academic_year')

res_nuts.columns = tidy_cols(res_nuts)

#Add SME and non-SME contract research
res_nuts['business_contract_research'] = res_nuts.iloc[:,0]+services_nuts.iloc[:,2]

make_indicator(res_nuts,'hebci',{'business_contract_research':'gbp_business_contract_research'},year_var='academic_year',decimals=0)


