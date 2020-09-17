import pandas as pd

from beis_indicators.utils import camel_to_snake



BASE_URL = ('https://www.hesa.ac.uk/data-and-analysis'
            '/providers/business-community')

def get_table(table_name, **read_opts):
    '''get_table
    '''
    df = pd.read_csv(f'{BASE_URL}/{table_name}', **read_opts)
    df['year'] = df['Academic Year'].str[:4].astype(int)
    return df

def get_service_income():
    """get_service_income
    """
    df = get_table('table-2a.csv', **{'header': 11})
    df = df[df['Unit'] == '£000s']

    con_fac_sme_income = df[
        (df['Type of organisation'] == "SME's") 
        & ((df['Type of service'] == 'Facilities and equipment related')
            | (df['Type of service'] == 'Consultancy'))]

    con_fac_non_sme_income = (df[
        (df['Type of organisation'] == "Other (non-SME) commercial businesses") 
        & ((df['Type of service'] == 'Facilities and equipment related')
            | (df['Type of service'] == 'Consultancy'))])

    res_non_sme_income = df[
        (df['Type of organisation'] == "Other (non-SME) commercial businesses") 
        & (df['Type of service'] == 'Contract research')]
    return df

