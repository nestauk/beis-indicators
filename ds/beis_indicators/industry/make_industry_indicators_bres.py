import logging
import pandas as pd
import beis_indicators
from beis_indicators.utils.dir_file_management_bres import (
    make_indicator,
    save_indicator,
)


PROJECT_DIR = beis_indicators.project_dir
INTERIM_PATH = f"{PROJECT_DIR}/data/interim/industry"
PROCESSED_PATH = f"{PROJECT_DIR}/data/processed/industry"

CULTURAL = beis_indicators.config["data"]["industries"]["cultural"]
HIGH_TECH = beis_indicators.config["data"]["industries"]["high_tech"]

YEARS = [2016, 2017, 2018, 2019]


def extract_segment(path, sector_list, sector_variable, sector_name):
    """Takes official data from a path and returns a segment of interest.
    We will use it to produce indicators about cultural activities in different NUTS2 regions.

    Arguments:
        path (str): path to csv
        sector_list (list of strs): is the list of codes we are interested in - could be segments or sectors
        sector_variable (str): is the variable that we use to identify sectors. It could be
                               the sic code or the Nesta segment.
        sector_name (str): name of sector e.g high tech

    """
    # activity in all sectors
    all_sectors = pd.read_csv(path, dtype={"SIC4": str})
    # activity in sector
    sector = all_sectors.loc[
        [x in sector_list for x in all_sectors[sector_variable]]
    ].reset_index(drop=True)
    # regroup and aggregate
    sector_agg = sector.groupby(["geo_nm", "geo_cd", "year"])["value"].sum()
    # add the name
    sector_agg.name = sector_name
    return pd.DataFrame(sector_agg)


def sector_location_quotient(path, sector_list, sector_variable, sector_name):
    """Calculates location quotient for sector of interest.
    The sector location quotient measures the regional concentration
    of employment for the sector of interest compared to nationally.

    Args:
        path (str): path to csv
        sector_list (list of strs): 'SIC4' codes or 'cluster_name's that define the sector
        sector_variable (str): the variable used to define sector, 'cluster_name' or 'SIC4'
        sector_name (str): name of sector e.g high tech
    """
    # activity in all sectors
    all_sectors = (
        pd.read_csv(path, dtype={"SIC4": str}, index_col=0)
        .groupby(["geo_nm", "geo_cd", "year"])["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "all_sectors"})
    )
    # activity in sector we are interested in
    sector = extract_segment(path, sector_list, sector_variable, sector_name)
    # merge activity in all sectors with sector we are interested in
    merged = pd.merge(sector, all_sectors, on=["geo_nm", "geo_cd", "year"])
    # location quotient numerator
    merged["lq_num"] = merged[sector_name] / merged["all_sectors"]
    # location quotient denominator
    merged["lq_denom"] = merged[sector_name].sum() / merged["all_sectors"].sum()
    # location quotient
    merged[f"location_quotient_{sector_name}"] = merged["lq_num"] / merged["lq_denom"]
    return merged.drop(
        columns=[sector_name, "all_sectors", "lq_num", "lq_denom"], inplace=False
    )


def _read_bres_file(y):
    """Reads the bres file for one year"""
    return f"{INTERIM_PATH}/nomis_BRES_{y}_TYPE450.csv"


if __name__ == "__main__":
    logger = logging.getLogger()
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)

    # make cultural employment indicator
    bres_cult = pd.concat(
        [
            extract_segment(
                _read_bres_file(y),
                CULTURAL,
                "cluster_name",
                "culture_entertainment_recreation",
            )
            for y in YEARS
        ]
    )
    ind_cult = make_indicator(
        bres_cult,
        {
            "culture_entertainment_recreation": "employment_culture_entertainment_recreation"
        },
        year_var="year",
        geo_type="nuts",
        geo_spec=2013,
        geo_var="geo_cd",
        decimals=0,
    )
    save_indicator(
        ind_cult,
        PROCESSED_PATH,
        "employment_culture_entertainment_recreation",
        "nuts2",
    )

    # make high tech employment indicator
    bres_high_tech = pd.concat(
        [
            extract_segment(
                _read_bres_file(y),
                HIGH_TECH,
                "SIC4",
                "high_tech",
            )
            for y in YEARS
        ]
    )
    ind_high_tech = make_indicator(
        bres_high_tech,
        {"high_tech": "employment_high_tech"},
        year_var="year",
        geo_type="nuts",
        geo_spec=2013,
        geo_var="geo_cd",
        decimals=0,
    )
    save_indicator(
        ind_high_tech,
        PROCESSED_PATH,
        "employment_high_tech",
        "nuts2",
    )

    # make location quotient high tech employment indicator
    bres_high_tech_quotient = pd.concat(
        [
            sector_location_quotient(
                _read_bres_file(y),
                HIGH_TECH,
                "SIC4",
                "high_tech",
            )
            for y in YEARS
        ]
    )
    ind_high_tech_quotient = make_indicator(
        bres_high_tech_quotient,
        {"location_quotient_high_tech": "location_quotient_high_tech"},
        year_var="year",
        geo_type="nuts",
        geo_spec=2013,
        geo_var="geo_cd",
        decimals=4,
    )
    save_indicator(
        ind_high_tech_quotient,
        PROCESSED_PATH,
        "location_quotient_high_tech",
        "nuts2",
    )

    # make indicator for economic complexity based on IDBR data
    # TYPE459- LEP, TYPE450- nuts2, TYPE449- nuts3
    compl = pd.read_csv(f"{INTERIM_PATH}/nomis_ECI_TYPE450.csv")
    ind_compl = make_indicator(
        compl.loc[
            (compl["source"] == "IDBR") & (compl["sector_type"] == "cluster_name")
        ],
        {"eci": "economic_complexity_index"},
        year_var="year",
        geo_type="nuts",
        geo_spec=2013,
        geo_var="geo_cd",
        decimals=4,
    )
    save_indicator(
        ind_compl,
        PROCESSED_PATH,
        "economic_complexity_index",
        "nuts2",
    )
