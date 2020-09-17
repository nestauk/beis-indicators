from dotenv import load_dotenv
import logging
import pandas as pd
import os
from sklearn.preprocessing import MultiLabelBinarizer
from sqlalchemy.engine.url import URL
from sqlalchemy.engine import create_engine

from beis_indicators import project_dir


logger = logging.getLogger(__name__)

GTR_RAW_DIR = f'{project_dir}/data/raw/crunchbase/'

load_dotenv()
url = URL(drivername='mysql+pymysql',
        username=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database='production')
engine = create_engine(url)


def get_cb_cats(engine):
    with open(f'{project_dir}/data/aux/cb_tech_groups.txt', 'r') as f:
	tech_groups = f.read().splitlines()

    cat_query = 'SELECT * FROM crunchbase_category_groups'
    df = pd.read_sql(cat_query, con=engine)
    df['category_groups_list'] = df['category_groups_list'].str.split(',')
    df = df[~pd.isnull(df['category_groups_list'])]

    mlb = MultiLabelBinarizer()
    mlb_vecs = mlb.fit_transform(df['category_groups_list'])
    mlb_df = pd.DataFrame(data=mlb_vecs, columns=mlb.classes_, index=df.index)

    tech_cats = mlb_df[mlb_df[tech_groups].sum(axis=1) > 0].index
    tech_cats = [t.lower() for t in tech_cats['name']]
    return tech_cats

def get_cb_uk_org_locs():
    org_loc_query = (
	"SELECT org.id, loc.id, loc.latitude, loc.longitude AS org_locs "
	"FROM "
	"(SELECT id, latitude, longitude FROM geographic_data "
	"WHERE country_alpha_3 = 'GBR') AS loc "
	"INNER JOIN "
	"(SELECT id, location_id FROM crunchbase_organizations "
	"WHERE closed_on IS NULL AND location_id IS NOT NULL AND roles = 'company') AS org "
	"ON (loc.id = org.location_id)")
    org_locs = pd.read_sql(org_query, con=engine)
    return org_locs

def get_tech_org_ids(cats):
    cat_list = ', '.join([f"'{t}'" for t in cats])
    org_cats_query = (
            "SELECT DISTINCT organization_id FROM crunchbase_category_groups "
            f"WHERE category_name IN ({cat_list})
            )
    df = pd.read_sql(org_cats_query, con=engine)



def get_cb_org_locs():
    """get_cb_org_locs
    """
    logger.info('Fetching CB organisation locations')
    org_query = ("SELECT project_id, latitude, longitude "
                 "FROM gtr_organisations_locations "
                 "INNER JOIN gtr_link_table "
                 "ON gtr_organisations_locations.id = gtr_link_table.id "
                 "WHERE gtr_link_table.rel = 'LEAD_ORG'")
    loc_query = ("SELECT id, latitude, longitude "
                "FROM geographic_data "
                "WHERE country_alpha_3 = 'GBR'")

    locs = pd.read_sql(loc_query, con=engine)

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

