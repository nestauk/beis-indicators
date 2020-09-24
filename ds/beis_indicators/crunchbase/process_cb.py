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
        "SELECT org.id, org.founded_on, loc.id AS location_id, loc.latitude, loc.longitude "
        "FROM "
        "(SELECT id, latitude, longitude FROM geographic_data "
        "WHERE country_alpha_3 = 'GBR') AS loc "
        "INNER JOIN "
        "(SELECT id, location_id, founded_on FROM crunchbase_organizations "
#       "WHERE closed_on IS NULL AND location_id IS NOT NULL AND roles = 'company') AS org "
        "WHERE location_id IS NOT NULL AND primary_role = 'company') AS org "
        "ON (loc.id = org.location_id)")
    org_locs = pd.read_sql(org_loc_query, con=engine)
    org_locs = org_locs.set_index('id')
    org_locs['year'] = pd.to_datetime(org_locs['founded_on'], errors='coerce').dt.year
    org_locs = org_locs.dropna(subset=['year'])
    org_locs = org_locs.drop('founded_on', axis=1)
    org_locs = org_locs[(org_locs['year'] > 2005) & (org_locs['year'] < 2019)]
    org_locs['companies_founded'] = 1
    return org_locs


def get_tech_org_ids():
    with open(f'{project_dir}/data/aux/cb_tech_groups.txt', 'r') as f:
        cats = f.read().splitlines()
    cat_list = ', '.join([f"'{t}'" for t in cats])
    org_cats_query = (
            "SELECT DISTINCT organization_id FROM crunchbase_organizations_categories "
            f"WHERE category_name IN ({cat_list})"
            )
    df = pd.read_sql(org_cats_query, con=engine)
    df = df['organization_id']
    return df


def get_cb_org_locs():
    """get_cb_org_locs
    """
    loc_query = ("SELECT id, latitude, longitude "
                "FROM geographic_data "
                "WHERE country_alpha_3 = 'GBR'")

    locs = pd.read_sql(loc_query, con=engine)
    return locs

def load_org_founded_counts():
    tech_ids = get_tech_org_ids()
    org_locs = get_cb_uk_org_locs()

    uk_tech_orgs = org_locs.reindex(tech_ids).dropna()
    uk_tech_orgs = (uk_tech_orgs
            .groupby(['location_id', 'year'])['companies_founded']
            .sum()
            .reset_index()
            .set_index('location_id'))

    uk_locs = org_locs[['latitude', 'longitude', 'location_id']]
    uk_locs = uk_locs.set_index('location_id').drop_duplicates()

    uk_tech_orgs = uk_tech_orgs.merge(uk_locs, left_index=True, right_index=True)
    return uk_tech_orgs
 
