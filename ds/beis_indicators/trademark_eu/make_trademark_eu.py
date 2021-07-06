import os
import requests
import pandas as pd
import eurostat as es
from zipfile import ZipFile
from io import BytesIO
import beis_indicators
import logging
from beis_indicators.utils.dir_file_management import make_indicator, save_indicator

PROJECT_DIR = beis_indicators.project_dir
TARGET_PATH = f"{PROJECT_DIR}/data/processed/trademark_eu"
YEARS = ["2010", "2013"]


def save_nuts_table(year, aux_path=f"{PROJECT_DIR}/data/aux/"):
    """Saves nuts table if does not exist already

    Args:
        year (str): year for which to download nuts table for
        aux_path (str): path to save nuts table to. Defaults to f'{PROJECT_DIR}/data/aux/'.
    """
    file = f"NUTS_{year}.xls"
    if os.path.exists(f"{aux_path}{file}") == False:
        nuts = requests.get(
            f"https://ec.europa.eu/eurostat/ramon/documents/nuts/NUTS_{year}.zip"
        )
        z = ZipFile(BytesIO(nuts.content))
        z.extract(file, path=aux_path)


def set_nuts_codes(year):
    """Set nuts2 and nuts3 country codes values in dictionary

    Args:
        year (str): year to set values for
    """
    nuts_table = pd.read_excel(f"{PROJECT_DIR}/data/aux/NUTS_{year}.xls")
    for l in [2, 3]:
        nuts_codes[year][l] = set(
            nuts_table.loc[
                (nuts_table["COUNTRY CODE"] == "UK") & (nuts_table["NUTS LEVEL"] == l)
            ]["NUTS CODE"]
        )


def create_nuts_list_spec(name):
    """Create nuts_list and nuts_spec from particular nuts
    codes as they were in a certain year. Dependent on whether
    patent is in the name.

    Args:
        name (str): descriptive name of data

    Returns:
        (list): list of relevant nuts codes
        (int): year for nuts_spec
    """
    if "patent" in name:
        nuts_list = nuts_codes["2010"][nuts_level]
        nuts_spec = 2010
    else:
        nuts_list = nuts_codes["2013"][nuts_level]
        nuts_spec = 2013
    return nuts_list, nuts_spec


def select_data(data, output_years):
    """Reformat data and select relevant years

    Args:
        data (pd.DataFrame): eurostat data
        output_years (list): years to output data for

    Returns:
        (pd.Dataframe): reformated and filtered data
    """
    output_years = str(output_years)
    return (
        data.loc[[x in nuts_list for x in data["geo\\time"]]]
        .reset_index(drop=True)
        .drop("unit", 1)
        .melt(id_vars="geo\\time")
        .query(f"variable in {output_years}")
    )


nuts_codes = {year: {} for year in YEARS}
for year in YEARS:
    # save nuts table if it does not exist already
    save_nuts_table(year)
    # populate dict with correct nuts2 and nuts3 country codes
    set_nuts_codes(year)

# collect the patent and trademark data from Eurostat
pats = es.get_data_df("pat_ep_rtot").query("unit == 'NR'")
high_tech_pats = es.get_data_df("pat_ep_rtec").query("unit == 'NR'")
# find years from columns
high_tech_pats_years = [col for col in high_tech_pats.columns if isinstance(col, int)]
# groupby sum to remove column for international patent classification (ipc)
high_tech_pats = (
    high_tech_pats.groupby(["unit", "geo\\time"])[high_tech_pats_years]
    .sum()
    .reset_index()
)
trades = es.get_data_df("ipr_ta_reg")

for nuts_level, level in zip([2], ["nuts2"]):
    for data, name in zip(
        [trades],
        [
            "eu_trademark_applications",
        ],
    ):
        # extract nuts codes and spec depending on the name (patents are 2010)
        nuts_list, nuts_spec = create_nuts_list_spec(name)
        # select the data, set date range to 2006 onwards
        sel = select_data(data, list(range(2006, 2025)))
        # make indicator
        ind = make_indicator(
            sel,
            {"value": name},
            year_var="variable",
            nuts_var="geo\\time",
            nuts_spec=nuts_spec,
        )
        # log max and min years in the data
        logging.info(str(min(ind["year"])))
        logging.info(str(max(ind["year"])))
        # save indicator
        save_indicator(ind, TARGET_PATH, f"{name}.{level}")
