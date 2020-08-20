import os
import logging
import pandas as pd
import requests
import numpy as np
import beis_indicators
from zipfile import ZipFile
import io
from beis_indicators.utils.dir_file_management import make_indicator, save_indicator
from beis_indicators.geo.reverse_geocoder import reverse_geocode
from beis_indicators.utils.dir_file_management import get_nuts_category


project_dir = beis_indicators.project_dir


# URLS and directories
nspl_target = f"{project_dir}/data/raw/nspl"
nspl_url = "https://www.arcgis.com/sharing/rest/content/items/ad7fd1d95f06431aaaceecdce4985c7e/data"
innovate_url = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/909140/20200801_Innovate_UK_Funded_Projects.xlsx'
innovate_path = f"{project_dir}/data/processed/innovate_uk"

target_path = f"{project_dir}/data/processed"

# Create a directory to save innovate indicators if it doesn't exist yet
if os.path.exists(innovate_path)==False:
    os.mkdir(innovate_path)

# Download the NSPL dataset (postcodes and geo) if necessary
if os.path.exists(f"{project_dir}/data/raw/nspl")==False:  
    logging.info("Downloading NSPL")
    nspl = requests.get(nspl_url)
    nspl_zip = ZipFile(io.BytesIO(nspl.content))
    nspl_zip.extractall(nspl_target)  

# Read NSPL data    
nspl = pd.read_csv(f"{nspl_target}/Data/NSPL_FEB_2020_UK.csv",
                  usecols=['pcds','lat','long'])

# Download and process the Innovate UK data
iuk = pd.read_excel(innovate_url)

iuk['year'] = [int(x.split('/')[0]) for x in iuk['Competition Year']]

iuk_recent = iuk.query("year >= 2010").dropna(
                            axis=0,subset=['year','Postcode'])
# Remove Withdrawn and on hold projects

iuk_recent = iuk_recent.loc[~iuk_recent['Project Status'].isin(
                                                    ['Withdrawn','On Hold'])]

# These are all the innovate UK postcodes
iuk_postcodes = set(iuk_recent ['Postcode'])

# Extract their lat, lon from nspl
iuk_pcs = nspl.loc[nspl['pcds'].isin(iuk_postcodes)]

# For each level in NUTS...
for level in ['2','3']:
    logging.info("Making indicator level {level}")

    # We do the reverse geocoding for all NUTS years in our interval (2010-2020)
    iuk_geo_pc = pd.concat(
                [reverse_geocode(iuk_pcs,f'nuts2_{str(y)}',
                    shape_file=f'NUTS_RG_01M_{str(y)}_4326_LEVL_{level}.shp.zip',
                    place_id='pcds',
                    coord_names=['long','lat'])['NUTS_ID'] 
                for y in [2010,2013,2016]],axis=1)

    iuk_geo_pc.columns = [f"nuts2_{str(y)}" for y in [2010,2013,2016]]
    
    # Turn the dataframe into a dict
    iuk_geo_pc_dict = iuk_geo_pc.to_dict(orient='index')
    
    # Assign NUTS to codes depending on the project year
    iuk_recent['nuts_code'] = [
            iuk_geo_pc_dict[row['Postcode']][get_nuts_category(row['year'])] if
            row['Postcode'] in iuk_geo_pc_dict.keys() 
            else np.nan for _id,row in iuk_recent.iterrows()]

    # Aggregate funding over year and postcode
    iuk_funding = iuk_recent.groupby(
        ['nuts_code','year'])['Grant Offered (£)'].sum().reset_index(name='GBP')
    # Make indicator
    ind = make_indicator(iuk_funding,{'GBP':'gbp_innovate_uk_funding'},
                         'year',nuts_var='nuts_code',decimals=0)
    # Save indicator
    save_indicator(ind,innovate_path,f"gbp_innovate_uk_funding.nuts{level}")