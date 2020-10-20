import logging
import numpy as np
import glob

from beis_indicators import project_dir

from beis_indicators.geo import NutsCoder, LepCoder
from beis_indicators.indicators import points_to_indicator, save_indicator
from beis_indicators.travel.travel_processing import get_travel_data

import pandas as pd

logger = logging.getLogger(__name__)



coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

BROADBAND_DIR = f'{project_dir}/data/raw/travel'



# MYDIR = (f'{project_dir}/data/raw/broadband')
# CHECK_FOLDER = os.path.isdir(MYDIR)

destinations = {'road_junctions': 'travel_to_road_junctions_average_time',
                'rail_stations': 'travel_to_rail_time',
                'airports': 'travel_to_airport_time'}

for destination,val_name in destinations.items():
    get_travel_data(destination)
    destination_df = pd.read_csv(f'{project_dir}/data/interim/{destination}_df.csv')
    for geo, coder in coders.items():
        time_mean = points_to_indicator(destination_df, value_col='RepTime', coder=coder,
                        aggfunc=np.mean, value_rename= val_name,
                        projection='EPSG:4326', x_col='lon', y_col='lat')
        # save_indicator(funding_agg, 'cordis', geo)
        time_mean = time_mean.sort_values(by=time_mean.columns[1])
        save_indicator(time_mean, 'travel', geo)
