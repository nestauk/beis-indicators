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
from beis_indicators.utils import chunks, camel_to_snake
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator

logger = logging.getLogger(__name__)


FRAMEWORK_PROGRAMMES = ['fp1', 'fp2', 'fp3', 'fp4', 'fp5', 'fp6', 'fp7', 'h2020']
CORDIS_DIR = f'{project_dir}/data/raw/cordis'


def prep_funding_data(fps=['h2020']):
    """prep_funding_data
    """
    
    project_dfs = []
    for fp in fps:
        projects = load_projects(fp)
        dates = load_dates(fp)
        projects = projects.merge(dates, left_on='rcn', right_on='rcn', how='inner')
        projects = projects[['year', 'ecContribution', 'lat', 'lon']]
        project_dfs.append(projects)

    projects = pd.concat(project_dfs)
    return projects


def get_cordis_projects(fp, extract=True, delete_raw=False):
    '''get_cordis_projects
    Download raw CORDIS projects in XML format for a given Framework Programme.

    Args:
        fp (str): Name of Framework Programme e.g. H2020 or FP1
        extract (bool): If True then extract projects from zipped XML to csv
        delete_raw (bool): If True then delete original zipped XML
    '''
    fp = fp.lower()
    logger.info(f'Downloading CORDIS projects for {fp.upper()}')

    url = f'https://cordis.europa.eu/data/cordis-{fp}projects-xml.zip'
    fname = url.split('/')[-1]
    cordis_dir = f'{project_dir}/data/raw/cordis'
    if not os.path.isdir(cordis_dir):
        os.mkdir(cordis_dir)
    fout = f'{cordis_dir}/{fname}'
    urlretrieve(url, fout)

    if extract:
        _extract_projects(fp, delete_raw=delete_raw)


def get_cordis_dates(fp):
    '''get_cordis_dates

    Args:
        fp (str): Name of Framework Programme
    '''
    base_url = 'https://cordis.europa.eu/data/{}'

    with open(f'{project_dir}/data/aux/cordis_url_suffixes.json', 'r') as f:
        cordis_url_suffixes = json.load(f)
    url = base_url.format(cordis_url_suffixes[fp]['projects'])
    read_opts = {"sep": ";", 
            "decimal": ",", 
            "parse_dates": ["startDate", "endDate"]}
    df = pd.read_csv(url, **read_opts)
    df = df[~pd.isnull(df['startDate'])]
    df['year'] = df['startDate'].dt.year.astype(int)
    df = df[['rcn', 'year']]
    df.to_csv(f'{CORDIS_DIR}/{fp}_project_dates.csv', index=False)


def load_dates(fp):
    '''load_dates
    Load a dataset of CORDIS project dates

    Args:
        fp(str): Name of Framework Programme

    Returns:
        (pd.DataFrame): Dataframe with project rcn codes and start year
    '''
    fin = f'{CORDIS_DIR}/{fp}_project_dates.csv'
    if not os.path.isfile(fin):
        get_cordis_dates(fp)
    df = pd.read_csv(fin)
    return df


def _extract_projects(fp, delete_raw=True):
    """_extract_projects
    Extracts UK projects from zip file downloaded from CORDIS.
    """

    logger.info(f'Parsing CORDIS {fp} projects. This might take a while.')
    project_zip_dir = f'{project_dir}/data/raw/cordis/cordis-{fp}projects-xml.zip'
    project_zip = ZipFile(project_zip_dir)

    projects = []
    for chunk in chunks(project_zip.namelist(), 1000):
        for file in chunk:

            project_xml = project_zip.open(file)
            soup = BeautifulSoup(project_xml, features='xml')
            parsed = _parse_xml_project(soup)
            
            rcn = file.split('-')[-1].split('_')[0]
            for p in parsed:
                p['rcn'] = rcn
            projects.extend(parsed)
    project_df = pd.DataFrame.from_records(projects)
    project_df = project_df[project_df['eu_code'] == 'UK']
    project_df.to_csv(f'{project_dir}/data/raw/cordis/{fp}_projects.csv', index=False)

    if delete_raw:
        os.remove(project_zip_dir)


def load_projects(fp, delete_raw=False):
    cordis_dir = f'{project_dir}/data/raw/cordis'
    csv_dir = f'{cordis_dir}/{fp}_projects.csv'

    if not os.path.isfile(csv_dir):
        if not os.path.isfile(xml_dir):
            get_cordis_projects(fp, extract=True, delete_raw=delete_raw)
        _extract_projects(fp, delete_raw=delete_raw)
        xml_dir = f'{project_dir}/data/raw/cordis/cordis-{fp}projects-xml.zip' 
    df = pd.read_csv(csv_dir)
    return df


def _get_tag_text(element, tag):
    d = element.find(tag)
    if d is not None:
        return d.text
    else:
        return None

def _parse_xml_project(soup):
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
