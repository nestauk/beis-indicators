import numpy as np
import logging

from beis_indicators import project_dir
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.crunchbase.process_cb import load_org_founded_counts


coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

founded = load_org_founded_counts()

for geo, coder in coders.items():
    total_companies = points_to_indicator(founded, value_col='companies_founded', 
            coder=coder, aggfunc=np.sum, projection='EPSG:4326', 
            x_col='longitude', y_col='latitude')
    save_indicator(total_companies, 'crunchbase', geo)

