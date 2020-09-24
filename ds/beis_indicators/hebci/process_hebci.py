import io
import pandas as pd
import requests

from beis_indicators import project_dir
from beis_indicators.utils import camel_to_snake


BASE_URL = ('https://www.hesa.ac.uk/data-and-analysis'
            '/providers/business-community')

def join_uni_locations(df):
    uni_geos = pd.read_csv(f'{project_dir}/data/raw/universities/uni_metadata.csv')
    uni_geos = uni_geos.set_index('UKPRN')
    uni_geos = uni_geos[['LATITUDE', 'LONGITUDE']]
    uni_geos.columns = [c.lower() for c in uni_geos.columns]

    df = df.merge(uni_geos, left_index=True, right_index=True, how='inner')
    return df


def get_table(table_name, **read_opts):
    '''get_table
    '''
    url = f'{BASE_URL}/{table_name}'
    response = requests.get(url)
    file = io.StringIO(response.content.decode('utf-8'))
    df = pd.read_csv(file, **read_opts)
    df['year'] = df['Academic Year'].str[:4].astype(int)
    return df


def _load_consultancy_facilities_sme(df):
    """_load_consultancy_facilities_sme
    
    Args:
        df (pd.DataFrame): Services income table from HESA (table-2a).

    Returns:
        df (pd.DataFrame): Consultancy and facilities income from SMEs.
    """
    df = df[df['Unit'] == '£000s']
    df = df[
        (df['Type of organisation'] == "SME's") 
        & ((df['Type of service'] == 'Facilities and equipment related')
            | (df['Type of service'] == 'Consultancy'))]
    df['Value'] = (df['Value'] * 1000).astype(int)
    return df


def _load_consultancy_facilities_non_sme(df):
    """_load_consultancy_facilities_non_sme
    
    Args:
        df (pd.DataFrame): Services income table from HESA (table-2a).

    Returns:
        df (pd.DataFrame): Consultancy and facilities income from commercial non-SMEs.
    """
    df = df[df['Unit'] == '£000s']
    df = df[
        (df['Type of organisation'] == "Other (non-SME) commercial businesses") 
        & ((df['Type of service'] == 'Facilities and equipment related')
            | (df['Type of service'] == 'Consultancy'))]
    df['Value'] = (df['Value'] * 1000).astype(int)
    return df


def _load_consultancy_facilities_public_third(df):
    """_load_consultancy_facilities_non_sme
    
    Args:
        df (pd.DataFrame): Services income table from HESA (table-2a).

    Returns:
        df (pd.DataFrame): Consultancy and facilities income from public and
            third sector organisations.
    """
    df = df[df['Unit'] == '£000s']
    df = (df[
        (df['Type of organisation'] == "Non-commercial organisations") 
        & ((df['Type of service'] == 'Facilities and equipment related')
            | (df['Type of service'] == 'Consultancy'))])
    df['Value'] = (df['Value'] * 1000).astype(int)
    return df


def _load_contract_research_sme(df):
    """_load_contract_research_sme
    
    Args:
        df (pd.DataFrame): Services income table from HESA (table-2a).

    Returns:
        df (pd.DataFrame): Contract research income from SMEs.
    """
    df = df[df['Unit'] == '£000s']
    df = df[
        (df['Type of organisation'] == "SME's") 
        & (df['Type of service'] == 'Contract research')]
    df['Value'] = (df['Value'] * 1000).astype(int)
    return df


def _load_contract_research_non_sme(df):
    """_load_contract_research_non_sme
    
    Args:
        df (pd.DataFrame): Services income table from HESA (table-2a).

    Returns:
        df (pd.DataFrame): Contract research income from non SME commercial
            organisations.
    """
    df = df[df['Unit'] == '£000s']
    df = df[
        (df['Type of organisation'] == "Other (non-SME) commercial businesses") 
        & (df['Type of service'] == 'Contract research')]
    df['Value'] = (df['Value'] * 1000).astype(int)
    return df


def _load_contract_research_public_third(df):
    """_load_contract_research_public_third
    
    Args:
        df (pd.DataFrame): Services income table from HESA (table-2a).

    Returns:
        df (pd.DataFrame): Contract research income from public and third
            sector organisations.
    """
    df = df[df['Unit'] == '£000s']
    df = df[
        (df['Type of organisation'] == "Non-commercial organisations") 
        & (df['Type of service'] == 'Contract research')]
    df['Value'] = (df['Value'] * 1000).astype(int)
    return df


def _load_cash(df):
    """_load_cash

    Args:
        df (pd.DataFrame): Collaborative research funding table from HESA (table-1).

    Returns:
        df (pd.DataFrame): Cash collaborative contributions as a proportion of public
            funding.
    """

    cash = df[
            (df['Type of income'] == 'Collaborative contribution - Cash')
            & (df['Source of public funding'] == 'All')]
    public_fund = df[
            (df['Type of income'] == 'Public funding')
            & (df['Source of public funding'] == 'All')]
    
    cash = cash.set_index(['UKPRN', 'year'])
    public_fund = public_fund.set_index(['UKPRN', 'year'])

    cash['Value'] = cash['Value'] / public_fund['Value']
    cash = cash.dropna(subset=['Value'])
    cash = cash.reset_index()
    return cash


def _load_regen_development(df):
    """_load_regen_development

    Args:
        df (pd.DataFrame): Regeneration and development income table from HESA
            (table-3).

    Returns:
        df (pd.DataFrame): Regeneration and development income from all sources.
    """
    df = df[df['Programme'] == 'Total programmes']
    df['Value'] = (df['Value'] * 1000).astype(int)
    return df


def load_hebci():
    read_opts = {'header': 11}
    df_service = get_table('table-2a.csv', **read_opts)
    df_service.rename(columns={'Number/Value': 'Value'}, inplace=True)
    df_collab = get_table('table-1.csv', **read_opts)
    df_regen = get_table('table-3.csv', **read_opts)

    dfs = {
        'consultancy_facilities_sme': _load_consultancy_facilities_sme(df_service),
        'consultancy_facilities_non_sme': _load_consultancy_facilities_non_sme(df_service),
        'consultancy_facilities_public_third': _load_consultancy_facilities_public_third(df_service),
        'contract_research_sme': _load_contract_research_sme(df_service),
        'contract_research_non_sme': _load_contract_research_non_sme(df_service),
        'contract_research_public_third': _load_contract_research_public_third(df_service),
        'cash_as_proportion_public_funding': _load_cash(df_collab),
        'regeneration_development': _load_regen_development(df_regen),
            }

    for name, df in dfs.items():
        df.set_index('UKPRN', inplace=True)
        df = join_uni_locations(df)
        dfs[name] = df[['Value', 'year', 'longitude', 'latitude']]

    return dfs

