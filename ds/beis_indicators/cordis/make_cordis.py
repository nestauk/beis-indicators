import logging
import numpy as np

from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.cordis.cordis_processing import prep_funding_data

import pandas as pd


logger = logging.getLogger(__name__)

var_name = f'cordis_funding'
aggfunc = np.sum
out_dir = 'cordis'
min_year = 2014
max_year = 2021

coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }


funding = prep_funding_data(fps=['h2020'])
funding = funding[(funding['year'] >= min_year) & (funding['year'] <= max_year)]
funding = funding.dropna()

for geo, coder in coders.items():
    funding_agg = points_to_indicator(funding, value_col='ecContribution', coder=coder,
                    aggfunc=aggfunc, value_rename=var_name,
                    projection='EPSG:4326', x_col='lon', y_col='lat')
    save_indicator(funding_agg, 'cordis', geo)

