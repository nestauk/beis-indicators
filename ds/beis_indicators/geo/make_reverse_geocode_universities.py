import pandas as pd

from beis_indicators import project_dir
from beis_indicators.geo.university_reverse_geocode import get_uni_metadata, reverse_geocode_unis

get_uni_metadata()
uni_meta = pd.read_csv(f'{project_dir}/data/raw/universities/uni_metadata.csv')
reverse_geocode_unis(uni_meta)
