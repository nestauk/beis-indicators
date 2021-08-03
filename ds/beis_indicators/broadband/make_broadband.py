import logging
import numpy as np
import glob

from beis_indicators import project_dir

from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.broadband.broadband_processing import main_run 

import pandas as pd

logger = logging.getLogger(__name__)

coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

BROADBAND_DIR = f'{project_dir}/data/raw/broadband'


files = glob.glob(f'{BROADBAND_DIR}/*.csv')

dfs = [pd.read_csv(f) for f in files]
latlon_speeds = pd.concat(dfs, ignore_index=True)

for geo, coder in coders.items():
    broadband_mean = points_to_indicator(latlon_speeds, value_col='speed', coder=coder,
                    aggfunc=np.mean, value_rename='broadband_download_speed_data',
                    projection='EPSG:4326', x_col='longitude', y_col='latitude')
    # save_indicator(funding_agg, 'cordis', geo)
    save_indicator(broadband_mean, 'broadband', geo)
