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
TARGET_PATH = f"{PROJECT_DIR}/data/processed/eurostat"
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


# create dict with year as keys and empty dicts as values
nuts_codes = {year: {} for year in YEARS}
for year in YEARS:
    # save nuts table if it does not exist already
    save_nuts_table(year)
    # populate dict with correct nuts2 and nuts3 country codes
    set_nuts_codes(year)

# Collect the patent and trademark data from Eurostat
pats = es.get_data_df("pat_ep_rtot").query("unit == 'NR'")
high_tech_pats = es.get_data_df("pat_ep_rtec").query("unit == 'NR'")
high_tech_pats_years = [col for col in high_tech_pats.columns if isinstance(col, int)]
high_tech_pats = (
    high_tech_pats.groupby(["unit", "geo\\time"])[high_tech_pats_years]
    .sum()
    .reset_index()
)
trades = es.get_data_df("ipr_ta_reg")

# For each NUTS codes list and name
for nuts_level, level in zip([2, 3], ["nuts2", "nuts3"]):
    # For each table and variable name
    for data, name in zip(
        [pats, high_tech_pats, trades],
        [
            "epo_patent_applications",
            "epo_hightech_patent_applications",
            "eu_trademark_applications",
        ],
    ):
        # Extract nuts codes depending on the variable (patents are 2010)
        if "patent" in name:
            nuts_list = nuts_codes["2010"][nuts_level]
        else:
            nuts_list = nuts_codes["2013"][nuts_level]

        # Select the data. We will focus on activity after 2005
        sel = (
            data.loc[[x in nuts_list for x in data["geo\\time"]]]
            .reset_index(drop=True)
            .drop("unit", 1)
            .melt(id_vars="geo\\time")
            .query("variable in [2006,2007,2008,2009,2010,2011,2012]")
        )

        # Make indicator
        if "patent" in name:
            nuts_spec = 2010
        else:
            nuts_spec = 2013

        ind = make_indicator(
            sel,
            {"value": name},
            year_var="variable",
            nuts_var="geo\\time",
            nuts_spec=nuts_spec,
        )

        logging.info(str(min(ind["year"])))
        logging.info(str(max(ind["year"])))

        # Save indicator
        save_indicator(ind, TARGET_PATH, f"{name}.{level}.TEST")
