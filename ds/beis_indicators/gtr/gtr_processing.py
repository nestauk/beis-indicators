from dotenv import load_dotenv
import logging
import pandas as pd
import os
from sqlalchemy.engine.url import URL
from sqlalchemy.engine import create_engine

from beis_indicators import project_dir


logger = logging.getLogger(__name__)

GTR_RAW_DIR = f'{project_dir}/data/raw/gtr/'

load_dotenv()
url = URL(drivername='mysql+pymysql',
          username=os.getenv('DB_USER'),
          password=os.getenv('DB_PASS'),
          host=os.getenv('DB_HOST'),
          port=os.getenv('DB_PORT'),
          database='production')
engine = create_engine(url)


def get_gtr_funding_by_loc():
    """get_gtr_funding_by_loc
    """
    logger.info('Fetching UKRI organisation locations')
    org_query = ("SELECT project_id, latitude, longitude "
                 "FROM gtr_organisations_locations "
                 "INNER JOIN gtr_link_table "
                 "ON gtr_organisations_locations.id = gtr_link_table.id "
                 "WHERE gtr_link_table.rel = 'LEAD_ORG'")
    logger.info('Fetching UKRI funding amounts')
    fund_query = ("SELECT project_id, gtr_funds.start, amount "
                "FROM gtr_funds "
                "INNER JOIN gtr_link_table "
                "ON gtr_funds.id = gtr_link_table.id "
                "WHERE gtr_funds.category = 'INCOME_ACTUAL'")

    funds = pd.read_sql(fund_query, con=engine)
    orgs = pd.read_sql(org_query, con=engine)

    data = pd.merge(funds, orgs, left_on='project_id', right_on='project_id', how='inner')
    data = data.dropna()
    data['year'] = data['start'].dt.year.astype(int)
    if not os.path.isdir(GTR_RAW_DIR):
        os.mkdir(GTR_RAW_DIR)
    fname = 'gtr_funding_by_location.csv'
    data.to_csv(f'{GTR_RAW_DIR}/{fname}', index=False)


def load_gtr_funding_by_loc(min_year=None, max_year=None):
    fname = f'{GTR_RAW_DIR}/gtr_funding_by_location.csv'
    if not os.path.isfile(fname):
        get_gtr_funding_by_loc()
    
    data = pd.read_csv(fname)
    if min_year is not None:
        data = data[data['year'] >= min_year]
    if max_year is not None:
        data = data[data['year'] <= max_year]
    return data

