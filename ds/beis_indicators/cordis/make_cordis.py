from bs4 import BeautifulSoup
import geopandas as gpd
import json
import logging
import numpy as np
import os
import pandas as pd
from urllib.request import urlretrieve
from zipfile import ZipFile

from beis_indicators import project_dir
from beis_indicators.utils.dir_file_management import save_indicator
from beis_indicators.utils import chunks
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator

logger = logging.getLogger(__name__)


FRAMEWORK_PROGRAMMES = ['fp1', 'fp2', 'fp3', 'fp4', 'fp5', 'fp6', 'fp7', 'h2020']

def _generate_project_path(fp):
    '''cordis_file_path
    Create the file path for a CORDIS dataset given a Framework Programme and 
    an entity such as projects or organizations.

    Args:
        fp_name (str): Name of Framework Programme
        resource_name (str): Entity type e.g., projects, organizations

    Returns:
        (str): File path 
    '''
    fname = f'{fp_name}_{resource_name}.csv'
    return f'{project_dir}/data/raw/cordis/{fp_name}/{fname}'


def get_cordis_projects(fp, extract=True, delete_raw=True):
    '''get_cordis_projects
    Download raw CORDIS projects in XML format for a given Framework Programme.

    Args:
        fp (str): Name of Framework Programme e.g. H2020 or FP1
    '''
    fp = fp.lower()
    url = f'https://cordis.europa.eu/data/cordis-{fp}projects-xml.zip'
    fname = base_url.split('/')[-1]
    cordis_dir = f'{project_dir}/data/raw/cordis'
    if not os.path.isdir(cordis_dir):
        os.mkdir(cordis_dir)
    fout = f'{cordis_dir}/{fname}'
    urlretrieve(url, fout)

    if extract:
        _extract_projects(fp, delete_raw=delete_raw)


def _extract_projects(fp, delete_raw=True):

    project_zip_dir = f'{project_dir}/data/raw/cordis/cordis-{fp}projects-xml.zip'
    project_zip = ZipFile(project_zip_dir)

    project_dfs = []
    for chunk in chunks(project_zip.namelist(), 1000):
        projects = {}
        for file in chunk:

            project_xml = project_zip.open(file)
            soup = BeautifulSoup(project_xml, features='xml')
            parsed = _parse_xml_project(soup)
            
            rcn = file.split('-')[-1].split('_')[0]
            for p in parsed:
                p['rcn'] = rcn
            projects.extend(parsed)
        dfs.append(pd.DataFrame.from_dict(projects))
    project_df = pd.concat(projects)
    project_df.to_csv(f'{project_dir}/data/raw/cordis/{fp}_projects.csv')

    if delete_raw:
        os.remove(project_zip_dir)


def load_projects(fp, delete_raw=True):
    cordis_dir = f'{project_dir}/data/raw/cordis'
    csv_dir = f'{cordis_dir}/{fp}_projects.csv'

    if not os.path.isfile(csv_dir):
        xml_dir = f'{project_dir}/data/raw/cordis/cordis-{fp}projects-xml.zip' 
        if not os.path.isfile(xml_dir):
            get_cordis_projects(fp, extract=True, delete_raw=delete_raw)
    df = pd.read_csv(csv_dir)
    return df


def _get_tag_text(element, tag):
    d = element.find(tag)
    if d is not None:
        return d.text
    else:
        return None

def _parse_xml_project(project_soup):
    orgs = soup.find_all('organization')
    orgs_parsed = []
    if len(orgs) > 0:
        for org in orgs:
            attrs = org.attrs #contains funding amount
            attrs['org_id'] = _get_tag_text(org, 'id')
            attrs['org_rcn'] = _get_tag_text(org, 'rcn')
            attrs['iso2_code'] = _get_tag_text(org, 'isoCode')
            attrs['eu_code'] = _get_tag_text(org, 'euCode')
            attrs['nuts_code'] = _get_tag_text(org, 'nutsCode')
            attrs['legal_name'] = _get_tag_text(org, 'legalName')
            attrs['short_name'] = _get_tag_text(org, 'shortName')
            org_type = _get_tag_text(org, 'code')
            if org_type is not None:
                attrs['org_type'] = org_type.replace('/', '')
            
            latlon = _get_tag_text(org, 'geolocation')
            if latlon is not None:
                latlon = latlon.split(',')
                lat = latlon[0]
                lon = latlon[1]
            else:
                lat = None
                lon = None
            attrs['lat'] = lat
            attrs['lon'] = lon
            orgs_parsed.append(attrs)
    else:
        orgs_parsed.append({})
    return orgs_parsed
