import json
import pandas as pd
import numpy as np

from beis_indicators.utils.set_utils import set_containment

NUTS_ENFORCED = {
    2003: 2003,
    2006: 2008,
    2010: 2012,
    2013: 2015,
    2016: 2018,
    2021: 2021,
}

NUTS_ENFORCED = {
    2003: 2003,
    2006: 2006,
    2010: 2010,
    2013: 2013,
    2016: 2016,
    2021: 2021,
}

NUTS2_UK_IDS ={
        2003: {'UKC2', 'UKK4', 'UKL2', 'UKG3', 'UKK2', 'UKD1', 'UKF2', 'UKG1', 
            'UKD3', 'UKH3', 'UKI1', 'UKJ4', 'UKM4', 'UKE2', 'UKI2', 'UKM1', 
            'UKJ1', 'UKJ3', 'UKM2', 'UKE4', 'UKE1', 'UKK1', 'UKE3', 'UKK3', 
            'UKG2', 'UKD2', 'UKL1', 'UKJ2', 'UKN0', 'UKH1', 'UKM3', 'UKH2', 
            'UKF3', 'UKD5', 'UKD4', 'UKC1', 'UKF1'}, 
        2006: {'UKC2', 'UKK4', 'UKL2', 'UKG3', 'UKK2', 'UKD1', 'UKF2', 'UKG1', 
            'UKD3', 'UKH3', 'UKI1', 'UKJ4', 'UKE2', 'UKI2', 'UKJ1', 'UKE4', 
            'UKM2', 'UKJ3', 'UKE1', 'UKK1', 'UKE3', 'UKK3', 'UKG2', 'UKM5', 
            'UKD2', 'UKL1', 'UKJ2', 'UKN0', 'UKH1', 'UKM3', 'UKF3', 'UKH2', 
            'UKD5', 'UKM6', 'UKD4', 'UKC1', 'UKF1'}, 
        2010: {'UKC2', 'UKK4', 'UKL2', 'UKG3', 'UKK2', 'UKD1', 'UKF2', 'UKG1', 
            'UKD3', 'UKH3', 'UKI1', 'UKJ4', 'UKE2', 'UKI2', 'UKJ1', 'UKE4', 
            'UKJ3', 'UKM2', 'UKE1', 'UKK1', 'UKE3', 'UKK3', 'UKG2', 'UKM5', 
            'UKL1', 'UKD7', 'UKJ2', 'UKN0', 'UKH1', 'UKM3', 'UKF3', 'UKH2', 
            'UKD4', 'UKM6', 'UKC1', 'UKD6', 'UKF1'}, 
        2013: {'UKC2', 'UKK4', 'UKL2', 'UKG3', 'UKK2', 'UKI6', 'UKD1', 'UKF2', 
            'UKI7', 'UKG1', 'UKD3', 'UKH3', 'UKJ4', 'UKE2', 'UKJ1', 'UKJ3', 
            'UKM2', 'UKE4', 'UKE1', 'UKK1', 'UKE3', 'UKI5', 'UKK3', 'UKG2', 
            'UKM5', 'UKL1', 'UKI4', 'UKD7', 'UKJ2', 'UKN0', 'UKH1', 'UKM3', 
            'UKH2', 'UKF3', 'UKD4', 'UKM6', 'UKI3', 'UKC1', 'UKD6', 'UKF1'}, 
        2016: {'UKM7', 'UKC2', 'UKM8', 'UKK4', 'UKL2', 'UKG3', 'UKK2', 'UKI6', 
            'UKD1', 'UKF2', 'UKI7', 'UKG1', 'UKD3', 'UKH3', 'UKJ4', 'UKE2', 
            'UKJ1', 'UKJ3', 'UKE4', 'UKE1', 'UKK1', 'UKE3', 'UKI5', 'UKM9', 
            'UKK3', 'UKG2', 'UKM5', 'UKL1', 'UKI4', 'UKD7', 'UKJ2', 'UKN0', 
            'UKH1', 'UKF3', 'UKH2', 'UKM6', 'UKD4', 'UKC1', 'UKI3', 'UKD6', 'UKF1'}}

NUTS_YEARS = np.array(list(NUTS2_UK_IDS.keys()))

def _year_containments(ids, years):
    containments = []
    for year in years:
        year_ids = NUTS2_UK_IDS[year]
        containments.append(set_containment(ids, year_ids))
    containments = np.array(containments)
    return containments

def nuts_earliest(year, mode='introduced'):
    '''nuts_earliest
    Returns the earliest possible NUTS version for a year
    based on the enforcement date.

    Args:
        year (int): A year
        mode (str): Choose whether to map years against the year that a NUTS
            version was enforced or introduced: Options:
                - `introduced` (default)
                - `enforced`
    Returns:
        earliest (int): The closest possible NUTS version year
    '''
    if mode == 'introduced':
        mapping = NUTS_INTRODUCED
    elif mode == 'enforced':
        mapping = NUTS_ENFORCED

    for k, v in mapping.items():
        if year >= v:
            earliest = k
    return earliest

def _detect_nuts2_uk(ids, year):
    '''detect_nuts
    Detects the most likely NUTS version based on the region IDs.
    '''
    earliest = nuts_earliest(year)
    years = NUTS_YEARS[NUTS_YEARS >= nuts_earliest(year)]
    # if only one year is possible, return it
    if len(years) == 1:
        return years[0]
    
    # if not calculate containments between region IDs from possible years
    containments = _year_containments(ids, years)
    # check if there is a single perfect match
    perfect = containments == 1
    if np.sum(perfect) == 1:
        year_inferred = years[np.argmax(perfect)]
        return year_inferred
    
    # if there is not a perfect match then chose the earliest and best
    # possible match
    elif np.sum(perfect) != 1:
        best = np.argwhere(containments == np.max(containments)).ravel()
        year_inferred = years[best[0]]
        return year_inferred

def auto_nuts2_uk(df, year='year', nuts_id='nuts_id'):
    '''auto_nuts
    Auto generates values for nuts_year_spec if they are not provided.
    
    Args:
        df (:obj:`pd.DataFrame`): Dataframe with indicator values.
        year (:obj:`str`): Column name for the indicator value year.
        nuts_id (:obj:`str`): Column name for the NUTS region IDs.
        
    Returns:
        df (:obj:`pd.DataFrame`): Modified dataframe with new column
            for NUTS region years, `nuts_year_spec`.
    '''
    dfs = []
    for year, group in df.groupby(year):
        auto_nuts_year = _detect_nuts2_uk(group[nuts_id], year)
        group = group.assign(nuts_year_spec=auto_nuts_year)
        dfs.append(group)

    df = pd.concat(dfs, axis=0)
    return df
