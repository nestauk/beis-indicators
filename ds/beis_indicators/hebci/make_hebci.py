import numpy as np
import logging

from beis_indicators import project_dir
from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.hebci.process_hebci import load_hebci


hebci_data = load_hebci()

coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

for name, data in hebci_data.items():
    for geo, coder in coders.items():
        indicator = points_to_indicator(data, value_col='Value', coder=coder,
                        aggfunc=np.sum, value_rename=name, dp=0,
                        projection='EPSG:4326', x_col='longitude', y_col='latitude')
        indicator[name] = indicator[name].astype(int)
        save_indicator(indicator, 'hebci', geo)

