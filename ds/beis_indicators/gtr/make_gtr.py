import pandas as pd
import os
from dotenv import load_dotenv
import beis_indicators
from beis_indicators.utils.dir_file_management import make_indicator, save_indicator
from beis_indicators.hesa.hesa_processing import multiple_nuts_estimates
from data_getters.core import get_engine
from data_getters.labs.core import download_file

from beis_indicators.geo.reverse_geocoder import reverse_geocode

PROJECT_DIR = beis_indicators.project_dir


def get_gtr(file, file_path, progress=True):
    """
    Fetch Gateway To Research predicted industries

    Repo: https://github.com/nestauk/gtr_data_processing
    Commit: cd3cddb
    File: https://github.com/nestauk/gtr_data_processing/blob/master/notebooks/05_jmg_data_demo.ipynb

    Args:
        file_path (`str`, optional): Path to download to. If None, stream file.
        progress (`bool`, optional): If `True` and `file_path` is not `None`,
            display download progress.
    """
    return download_file(
        file_to_fetch=file, download_path=file_path + file, progress=progress
    )


def multi_geocode(source_df, lon_lat, ent_id, years):
    """
    Function that extracts the nuts2 region for a location in multiple years

    Args:
        source_df (pandas dataframe) with longitude and latitude we want to geocode
        lon_lat (list) with the names of the longitude and latitude variables
        ent_id (str) is the column we use to identify the entity we are reverse geocoding
        years (str) are the nuts years we want to extract

    Returns a dict where the keys are the ids for a place and the values are dicts for different
    nuts years
    """
    nutified = [
        reverse_geocode(
            place_df=source_df,
            shape_name=f"nuts2_{str(y)}",
            shape_file=f"NUTS_RG_01M_{str(y)}_4326_LEVL_2.shp.zip",
            place_id=ent_id,
            coord_names=lon_lat,
        )["NUTS_ID"]
        for y in years
    ]

    # create a df and turn into a dict
    nutified_df = pd.concat(nutified, axis=1)
    nutified_df.columns = [f"nuts2_{str(y)}" for y in years]
    nutified_dict = nutified_df.to_dict(orient="index")
    return nutified_dict


#########
# 1. COLLECT DATA
#########

# load the sql credentials to collect data from DAPS
load_dotenv()
sql_creds = os.getenv("config_path")

# create connection
con = get_engine(sql_creds)

# collect organisations-locations
orgs_locs = pd.read_sql("gtr_organisations_locations", con=con, chunksize=1000)
orgs_locs_df = pd.concat(orgs_locs)

# collect projects (with discipline predictions and funding) if needed
if os.path.exists(f"{PROJECT_DIR}/data/raw/gtr/17_9_2019_gtr_projects.csv") == False:
    get_gtr(
        file="17_9_2019_gtr_projects.csv",
        file_path=f"{PROJECT_DIR}/data/raw/gtr/",
        progress=False,
    )

# read projects
gtr_proj = pd.read_csv(
    f"{PROJECT_DIR}/data/raw/gtr/17_9_2019_gtr_projects.csv", dtype={"id": str}
)

# keep relevant variables
gtr_proj_short = gtr_proj[["project_id", "year", "amount", "disc_top"]]

# collect link_table connecting orgs to projects
# (this step takes a while)
gtr_link = pd.read_sql("gtr_link_table", con=con, chunksize=1000)
gtr_link_df = pd.concat(gtr_link)
link_orgs = gtr_link_df.loc[gtr_link_df["rel"] == "LEAD_ORG"]

# this is the set of organisations that lead projects
lead_org_id = set(link_orgs["id"])

###########
# 2. PROCESS DATA
###########

# create the org-nuts lookup
# focus on organisations that lead projects
org_locs_lead = orgs_locs_df.loc[
    [x in lead_org_id for x in orgs_locs_df["id"]]
].reset_index(drop=False)

# create the nuts lookup
orgs_nuts = multi_geocode(
    org_locs_lead, ["longitude", "latitude"], "id", [2010, 2013, 2016]
)

# merge projects with organisations
proj_org = pd.merge(
    gtr_proj_short,
    link_orgs[["project_id", "id"]],
    left_on="project_id",
    right_on="project_id",
).query("year >= 2010")

##############
# 3. CREATE AND SAVE INDICATORS
##############

# create the NUTS estimates
nuts_est = multiple_nuts_estimates(
    proj_org,
    orgs_nuts,
    set(proj_org["disc_top"]),
    "disc_top",
    "amount",
    year_var="year",
    my_id="id",
).fillna(0)

# sum total for all disciplines
all_nuts_est = nuts_est.sum(axis=1)
all_nuts_est.name = "total_gtr_projects_all_disciplines"
# make indicator for all disciplines
ind_all = make_indicator(
    all_nuts_est,
    {"total_gtr_projects_all_disciplines": "total_gtr_projects_all_disciplines"},
    "year",
)
# save indicator for all disciplines
save_indicator(
    ind_all,
    target_path=f"{PROJECT_DIR}/data/processed/gtr",
    var_name="total_gtr_projects_all_disciplines",
)

# load list of STEM disciplines
with open(f"{PROJECT_DIR}/data/aux/stem_gtr.txt", "r") as infile:
    stem = infile.read().split("\n")
# create stem discipline aggregation
stem_nuts_est = nuts_est[stem].sum(axis=1)
stem_nuts_est.name = "total_gtr_projects_stem"
# make stem indicator
ind_stem = make_indicator(
    stem_nuts_est, {"total_gtr_projects_stem": "total_gtr_projects_stem"}, "year"
)
# save stem indicator
save_indicator(
    ind_stem,
    target_path=f"{PROJECT_DIR}/data/processed/gtr",
    var_name="total_gtr_projects_stem",
)
