import pandas as pd
import beis_indicators

PROJECT_DIR = beis_indicators.project_dir
NI_BRES_2019_PUB_TABLES = "https://www.nisra.gov.uk/sites/nisra.gov.uk/files/publications/BRES2019-Publication-Tables.xlsx"


def sic4_to_cluster_lookup(
    sic4_lookup_csv=f"{PROJECT_DIR}/data/raw/sic_4_industry_segment_lookup.csv",
):
    """Use SIC4 to cluster namelookup csv file to create a dictionary
    with SIC4 as keys, cluster_name as values"""
    lookup = pd.read_csv(sic4_lookup_csv)
    return dict(zip(lookup.sic_4, lookup.cluster))


def read_ni_data(pub_table=NI_BRES_2019_PUB_TABLES):
    """Read Northern Ireland BRES publication table
    xlsx file, sheet named 'SIC4' and return a dataframe

    Args:
        pub_table (xlsx): Northern Ireland BRES publication table.
                        Defaults to NI_BRES_2019_PUB_TABLES.

    Returns:
        (dataframe): number of employees for each SIC4 code in Northern Ireland
    """

    return pd.read_excel(
        pub_table,
        sheet_name="SIC4",
        header=4,
    )


def process_ni_data(
    pub_table,
    lookup,
    year=2019,
    geo_type="nuts 2013 level 2",
    geo_cd="UKN0",
    geo_nm="Northern Ireland",
):
    """Process NI data into the same format as nomis_BRES_2019_TYPE450.csv

    Args:
        pub_table (dataframe): number of employees for each SIC4 code in Northern Ireland
        lookup (dict): keys = SIC4 code, values = cluster_name
        geo_type (str): nuts year and level
        geo_cd (str): geographical code
        geo_nm (str): geographical name

    Returns:
        (dataframe): dataframe in the same format as nomis_BRES_2019_TYPE450.csv
    """
    pub_table = (
        pub_table.loc[:, ["SIC 2007", "Total"]]
        .dropna()
        .drop(pub_table[pub_table["SIC 2007"] == "Total"].index)
        .astype({"SIC 2007": "int64"})
        .replace("*", 0)
        .rename(columns={"SIC 2007": "SIC4", "Total": "value"})
        .assign(year=year, geo_type=geo_type, geo_cd=geo_cd, geo_nm=geo_nm)
    )
    pub_table["cluster_name"] = pub_table["SIC4"].map(lookup)
    return pub_table


def add_ni_to_nomis_bres(nomis_bres, ni_df, save_path):
    """Concat nomis_BRES df with NI df and save csv"""
    pd.concat([nomis_bres, ni_df]).reset_index(drop=True).to_csv(save_path, index=True)
