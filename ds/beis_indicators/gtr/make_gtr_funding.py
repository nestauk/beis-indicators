import numpy as np
import logging

from beis_indicators import project_dir
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.gtr.gtr_processing import load_gtr_funding_by_loc


var_name = 'total_ukri_funding'

coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

funding = load_gtr_funding_by_loc(min_year=2006, max_year=2019)

for geo, coder in coders.items():
    total_funding = points_to_indicator(funding, value_col='amount', coder=coder,
                    aggfunc=np.mean, value_rename=var_name,
                    projection='EPSG:4326', x_col='longitude', y_col='latitude')
    save_indicator(total_funding, 'gtr', geo)
