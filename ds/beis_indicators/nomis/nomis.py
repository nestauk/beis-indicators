from io import StringIO
import requests
import os
import logging
import ratelim
from numpy import arange, sum
from pandas import concat, crosstab, melt, read_csv, read_excel
import pandas as pd
import beis_indicators
from beis_indicators.utils.pandas import preview
from beis_indicators.utils.dir_file_management import make_dirs
from beis_indicators.nomis.ni_processing import (
    sic4_to_cluster_lookup,
    read_ni_data,
    process_ni_data,
    add_ni_to_nomis_bres,
)

logger = logging.getLogger(__name__)
CELL_LIMIT = 25_000
REQUESTS_PER_SECOND = 2

PROJECT_DIR = beis_indicators.project_dir
BRES_2019_450 = f"{PROJECT_DIR}/data/interim/industry/nomis_BRES_2019_TYPE450.csv"


def _zero_pad(x, column, width=4):
    """Zero pad SIC4 codes missing leading zeros, such as 161"""
    x[column] = x[column].astype(str).apply(lambda x: x.zfill(width))
    return x


def make_nomis(geo_type, year_l, project_dir=None):
    """Make NOMIS BRES & IDBR datasets

    Args:
        geo_type (str): Geography type to consider.
            Options: 'lad' or 'ttwa'.
        year_l (list[int]): Year of data to consider
        project_dir (str): Project path
    """

    if project_dir is None:
        project_dir = beis_indicators.project_dir

    make_dirs("industry", ["raw", "interim"])

    # SIC4 <-> Nesta segement lookup
    fin = f"{beis_indicators.project_dir}/data/raw/sic_4_industry_segment_lookup.csv"
    segments = (
        read_csv(fin, usecols=["sic_4", "cluster"])
        .pipe(_zero_pad, "sic_4")
        .rename(columns={"sic_4": "SIC4", "cluster": "cluster_name"})
        .pipe(preview)
    )

    for dataset in ["BRES", "IDBR"]:
        for year in year_l:
            raw_fout = (
                f"{project_dir}/data/raw/industry/nomis_{dataset}_{year}_{geo_type}.csv"
            )
            tidy_fout = f"{project_dir}/data/interim/industry/nomis_{dataset}_{year}_{geo_type}.csv"

            # Fetch and save raw data if not present
            if os.path.exists(raw_fout):
                df = read_csv(raw_fout)
            else:
                df = get_nomis(dataset, geo_type, year)
                df.to_csv(raw_fout, index=False)

            # Pivot to [Region x Sector] matrices
            logger.info(f"Pivoting {dataset} for {year} and {geo_type}")
            (  # Clean and enrich with industrial segments
                df.rename(
                    columns={
                        "DATE_NAME": "year",
                        "INDUSTRY_NAME": "SIC4",
                        "GEOGRAPHY_TYPE": "geo_type",
                        "OBS_VALUE": "value",
                    }
                )
                .drop(["OBS_STATUS_NAME", "RECORD_COUNT"], 1)
                .assign(SIC4=lambda x: x["SIC4"].str.extract("([0-9]*)"))
                .merge(segments, on="SIC4")  # Merge onto remapping
                .pipe(preview)
                .fillna(0)
                .to_csv(tidy_fout)
            )


def get_nomis(dataset, geo_type, year):
    """Get BRES or IDBR datasets (SIC4) from NOMIS for given year and geography

    Args:
        dataset (str, {'BRES', 'IDBR'}): BRES or IDBR
        geo_type (str, {'TTWA', 'LAD', 'TYPE{int}'}): Geography type.
            'TTWA', 'LAD', or geography type to be passed straight to the API query.
            For example `TYPE450` will give 2013 NUTS2 areas.
        year (int): Year

    Returns:
        pandas.DataFrame

    Notes:

        NOMIS data-set ID's:
            141: UK Business Counts - local units by industry and employment
                size band (2010 onwards)
            172: Business Register and Employment Survey : open access
                (2015 onwards)
            189: Business Register and Employment Survey (excluding units
                registered for PAYE only) : open access (2009 to 2015)
    """

    logger.info(f"Fetching {dataset} for {year} and {geo_type}")

    if dataset == "IDBR":
        data_id = 141
        API_cols = "&employment_sizeband=0&legal_status=0&measures=20100"
    elif dataset == "BRES" and year >= 2015:
        data_id = 189
        API_cols = "&employment_status=4&measure=1&measures=20100"
    elif dataset == "BRES" and 2009 <= year < 2015:
        data_id = 172
        API_cols = "&employment_status=4&measure=1&measures=20100"
    API_start = f"http://www.nomisweb.co.uk/api/v01/dataset/NM_{data_id}_1.data.csv"

    # LAD, TTWA geography queries of API
    if geo_type == "LAD":
        API_geo = "?geography=TYPE434"
    elif geo_type == "TTWA":
        API_geo = "?geography=TYPE447"
    elif geo_type.startswith("TYPE") and _check_geo_type_suffix(geo_type[4:]):
        API_geo = f"?geography={geo_type}"
    else:
        raise ValueError(f"`geo_type` value {geo_type} not valid")
    # 4 digit SIC query codes for NOMIS
    with open(f"{beis_indicators.project_dir}/data/aux/NOMIS_4SIC_codes.txt") as f:
        codes = f.read().rstrip("\n")
    API_4SIC = f"&industry={codes}"

    API_year = f"&date={year}"

    fields = [
        "date_name",
        "geography_type",
        "geography_name",
        "geography_code",
        "industry_name",
        "obs_value",
        "obs_status_name",
        "record_count",
    ]
    API_select = f"&select={','.join(fields)}"
    column_map = {"GEOGRAPHY_NAME": "geo_nm", "GEOGRAPHY_CODE": "geo_cd"}

    query = API_start + API_geo + API_year + API_4SIC + API_cols + API_select
    return query_nomis(query).rename(columns=column_map)


def make_gva(project_dir, year):
    """Make and save dataset of GVA per capita

    Args:
        project_dir (str):
            Path to project directory
        year (int):
            Year for which to use GVA estimate
    """

    gva_fin = f"{project_dir}/data/external/gva_pc.xls"
    gva_fout = f"{project_dir}/data/interim/gva_pc.csv"

    columns = {"LAU1 code": "lad_cd", "LA name": "lad_nm"}
    df = (
        read_excel(gva_fin, sheet_name="GVA per head", skiprows=2)
        # Rename columns
        .rename(columns=str)
        .rename(columns=columns)
        .pipe(
            melt,
            id_vars=["lad_cd", "lad_nm"],
            value_vars=arange(1997, 2016).astype(str),
            var_name="year",
            value_name="gva_pc",
        )
    )

    df.to_csv(gva_fout)


def make_lad_ttwa_map(project_dir):
    """Make lookup between TTWA's and LAD's

    Args:
        project_dir (str, optional):
            Path to project directory
    """

    if project_dir is None:
        project_dir = beis_indicators.project_dir

    nspl_fin = f"{project_dir}/data/raw/nspl.csv"
    table_fout = f"{project_dir}/data/processed/lad_ttwa_lookup.csv"

    # LOAD NSPL
    nspl_cols = {"pcds": "postcode", "laua": "lad", "ttwa": "ttwa"}

    nspl = read_csv(nspl_fin, usecols=nspl_cols.keys()).rename(columns=nspl_cols)

    lookup_table = (  # Find overlap between TTWA and LAD
        crosstab(nspl.ttwa, nspl.lad, normalize="index")
        .reset_index(drop=False)
        .pipe(melt, id_vars="ttwa")
        .sort_values("ttwa")
    )

    lookup_table.to_csv(table_fout)


@ratelim.patient(REQUESTS_PER_SECOND, time_interval=1)
def query_nomis(link, offset_size=CELL_LIMIT):
    """Query NOMIS api with ratelimiting and pagination

    Args:
        link (str): URL of NOMIS API query
        offset_size (int): Size of pagination chunks

    Returns:
        pandas.DataFrame
    """
    logger.info(f"Getting: {link}")

    df_container = []
    offset = 0
    first_page = True
    records_left = 1  # dummy

    # While the final record we will obtain is below the total number of records:
    while records_left > 0:
        # Modify the query link with the offset
        query = link + "&recordoffset={off}".format(off=str(offset))

        response = requests.get(query)
        response.raise_for_status()
        if response.text == "":
            raise ValueError(f"Empty response for query: {query}")

        # Run query and store
        df_container.append(read_csv(StringIO(response.text)))

        # Update the offset (next time we will query from this point)
        offset += offset_size

        # Get number of records from first iteration
        if first_page:
            total_records = df_container[-1].RECORD_COUNT.values[0]
            logger.info(f"{total_records} to download")
            records_left = total_records
            first_page = False

        records_left -= offset_size
        logger.info(f"{records_left} records left")

    # Concatenate all the outputs
    return concat(df_container)


def pivot_area_industry(df, sector, aggfunc=sum):
    """Convert BRES/IDBR data at SIC4 level to pivot table

    Fill missing values with zero
    Convert to pivot table with rows as regions and columns as SIC

    Args:
        df (pandas.DataFrame): Raw BRES/IDBR data - one row per area-sector pair
            Expected Columns: `{"GEOGRAPHY_TYPE", "geo_nm", "geo_cd",
            sector, "OBS_VALUE", "RECORD_COUNT", "OBS_STATUS_NAME"}`.
        sector (str): Column of the sector type to pivot on
        agg_func (function, optional): Aggregation function passed to
            `pandas.DataFrame.pivot_table`.

    Returns:
        pandas.DataFrame: [number areas x number sectors]

    """

    df_piv = (
        df
        # Fill missing values with zeros
        .fillna(0)
        # Pivot to [areas x sectors]
        .pivot_table(
            index=["geo_cd", "geo_nm"],
            columns=sector,
            values="value",
            fill_value=0,
            aggfunc=aggfunc,
        )
    )

    return df_piv


def lad_to_ttwa(data, index, id_vars, project_dir=None):
    """Convert data[col] index by LAD to TTWA

    Args:
        data (pandas.DataFrame): Input DataFrame
        index (str): Column contains LAD ID
        id_vars (list[str]): Columns to transform
        project_dir (str, optional): Path to project directory

    Returns:
        pandas.DataFrame
    """

    if project_dir is None:
        project_dir = beis_indicators.project_dir

    if id_vars is None:
        id_vars = data.columns.values

    table_fin = f"{project_dir}/data/processed/lad_ttwa_lookup.csv"
    lookup_table = read_csv(table_fin)

    def weight(x, id_vars):
        x[id_vars] *= x["value"].values.reshape(-1, 1)
        return x

    df = (
        lookup_table.merge(data, left_on="lad", right_on=index)
        .pipe(weight, id_vars)  # Apply weighting
        # Sum over ttwa for `id_vars`
        .groupby("ttwa")
        .agg({k: "sum" for k in id_vars})
        .reset_index(drop=False)
    )

    return df


def _check_geo_type_suffix(x):
    """Checks if `geo_type` suffix contains an `int`"""
    try:
        return int(x)
    except:
        raise ValueError(f"`geo_type` suffix: '{x}' cannot be parsed as `int`.")


if __name__ == "__main__":
    # make nomis
    conf = beis_indicators.config["data"]["nomis"]
    geo_type = conf["geography"].upper()
    years = conf["years"]
    make_nomis(geo_type, years)
    # add NI data to nomis_BRES_2019_TYPE450.csv (data only available for 2019)
    if geo_type == "TYPE450":
        ni_df = process_ni_data(
            pub_table=read_ni_data(), lookup=sic4_to_cluster_lookup()
        )
        add_ni_to_nomis_bres(
            nomis_bres=pd.read_csv(BRES_2019_450, index_col=[0]),
            ni_df=ni_df,
            save_path=BRES_2019_450,
        )
