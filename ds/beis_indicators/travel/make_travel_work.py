import logging
import numpy as np
import glob

from beis_indicators import project_dir

from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.travel.travel_work_processing import get_travel_work_data

import pandas as pd

logger = logging.getLogger(__name__)



coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

get_travel_work_data()
destination_df = pd.read_csv(f'{project_dir}/data/interim/travel_to_work_all_years.csv')
for geo, coder in coders.items():
    time_mean = points_to_indicator(destination_df, value_col='Mean', coder=coder,
                    aggfunc=np.mean, value_rename= 'Mean',
                    projection='EPSG:4326', x_col='long', y_col='lat')
    if geo == 'lep':
        time_mean = time_mean.rename(columns = {'Mean': 'travel_to_work_times_average'}).sort_values(['lep_id', 'year']).reset_index(drop=True)
    else:
        time_mean = time_mean.rename(columns = {'Mean': 'travel_to_work_times_average'}).sort_values(['nuts_id', 'year']).reset_index(drop=True)


    # print(time_mean.head())
    save_indicator(time_mean, 'travel', geo)
