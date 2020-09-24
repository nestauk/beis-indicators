import numpy as np
import logging

from beis_indicators import project_dir
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.hebci.process_hebci import load_hebci


coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

hebci_data = load_hebci()

aggfuncs = {
        'consultancy_facilities_sme': np.sum,
        'consultancy_facilities_non_sme': np.sum,
        'consultancy_facilities_public_third': np.sum, 
        'contract_research_sme': np.sum,
        'contract_research_non_sme': np.sum, 
        'contract_research_public_third': np.sum,
        'cash_as_proportion_public_funding': np.mean,
        'regeneration_development': np.sum, 
        }


for name, data in hebci_data.items():
    for geo, coder in coders.items():
        indicator = points_to_indicator(data, value_col='Value', coder=coder,
                        aggfunc=aggfuncs[name], value_rename=name,
                        projection='EPSG:4326', x_col='longitude', y_col='latitude')
        save_indicator(indicator, 'hebci', geo)
