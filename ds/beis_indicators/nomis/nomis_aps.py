"""
"""
from io import StringIO
import requests
import os
import logging

import ratelim
from numpy import arange, sum
from pandas import concat, crosstab, melt, read_csv, read_excel
from beis_indicators import project_dir


import beis_indicators
from beis_indicators.utils.pandas import preview

logger = logging.getLogger(__name__)
CELL_LIMIT = 25_000
REQUESTS_PER_SECOND = 2



def make_nomis(geo_type, year_l, project_dir=None):
    """ Make NOMIS BRES & IDBR datasets

    Args:
        geo_type (str): Geography type to consider.
            Options: 'lad' or 'ttwa'.
        year_l (list[int]): Year of data to consider
        project_dir (str): Project path
    """

    if project_dir is None:
        project_dir = beis_indicators.project_dir

    # # SIC4 <-> Nesta segement lookup
    # fin = f"{beis_indicators.project_dir}/data/raw/sic_4_industry_segment_lookup.csv"
    # segments = (
    #     read_csv(fin, usecols=["sic_4", "cluster"])
    #     .pipe(_zero_pad, "sic_4")
    #     .rename(columns={"sic_4": "SIC4", "cluster": "cluster_name"})
    #     .pipe(preview)
    # )
    if geo_type == 'nuts':
        types = [beis_indicators.config["data"]["aps"]["geography"]["nuts2010"]["nuts2"],
        beis_indicators.config["data"]["aps"]["geography"]["nuts2010"]["nuts3"],
        beis_indicators.config["data"]["aps"]["geography"]["nuts2013"]["nuts2"],
        beis_indicators.config["data"]["aps"]["geography"]["nuts2013"]["nuts3"],
        beis_indicators.config["data"]["aps"]["geography"]["nuts2016"]["nuts2"],
        beis_indicators.config["data"]["aps"]["geography"]["nuts2016"]["nuts3"]
        ]

    elif geo_type == 'lep':
        types = [beis_indicators.config["data"]["aps"]["geography"]["lep"]]

    for dataset in ["ECON_ACTIVE_NVQ_PRO", "ECON_ACTIVE_STEM_PRO", "STEM_DENSITY", "PRO_OCCS"]:
        # print(nuts_year)
        for year in year_l:
            for type in types:

            # print(geo_type)
      # for each year, just go through all of them
                raw_fout = (
                    f"{project_dir}/data/raw/aps/aps_{dataset}_{year}_{type}.csv"
                )
                tidy_fout = (
                    f"{project_dir}/data/interim/aps/aps_{dataset}_{year}_{type}.csv"
                )

                # Fetch and save raw data if not present
                if os.path.exists(raw_fout):
                    df = read_csv(raw_fout)
                else:
                    df = get_nomis(dataset, type, year)
                    df.to_csv(raw_fout, index=False)

            # # Pivot to [Region x Sector] matrices
            # logger.info(f"Pivoting {dataset} for {year} and {geo_type}")
            # (
            #     df.rename(
            #         columns={
            #             "DATE_NAME": "year",
            #             "GEOGRAPHY_TYPE": "geo_type",
            #             "OBS_VALUE": "value",
            #         }
            #     )
            #     .drop(["OBS_STATUS_NAME", "RECORD_COUNT"], 1)
            #     .pipe(preview)
            #     .fillna(0)
            #     .to_csv(tidy_fout)
            # )


def get_nomis(dataset, geo_type, year):
    """ Get BRES or IDBR datasets (SIC4) from NOMIS for given year and geography

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
    # geo_type = type
    logger.info(f"Fetching {dataset} for {year} and {geo_type}")

    if dataset == "ECON_ACTIVE_NVQ_PRO":
        data_id = 17
        tail_id = 5
        API_cols = "&variable=546&measures=20599,21001,21002,21003"
    elif dataset == "ECON_ACTIVE_STEM_PRO":
        data_id = 17
        tail_id = 1
        API_cols = "&cell=404882177,404883201&measures=20100,20701"
    elif dataset == "STEM_DENSITY":
        data_id = 17
        tail_id = 5
        API_cols = "&variable=1543&measures=20599,21001,21002,21003"
    elif dataset == "PRO_OCCS":
        data_id = 17
        tail_id = 5
        API_cols = "&variable=1533&measures=20599,21001,21002,21003"


    API_start = f"http://www.nomisweb.co.uk/api/v01/dataset/NM_{data_id}_{tail_id}.data.csv"

    # LAD, TTWA geography queries of API

    if geo_type == "LAD":
        API_geo = "?geography=TYPE434"
    elif geo_type == "TTWA":
        API_geo = "?geography=TYPE447"
    elif geo_type.startswith("TYPE") and _check_geo_type_suffix(geo_type[4:]):
        API_geo = f"?geography={geo_type}"
    else:
        raise ValueError(f"`geo_type` value {geo_type} not valid")

    # if year >= 2013 and year < 2016:
    #     if geo_type == "LAD":
    #         API_geo = "?geography=TYPE434"
    #     elif geo_type == "TTWA":
    #         API_geo = "?geography=TYPE447"
    #     elif geo_type.startswith("TYPE") and _check_geo_type_suffix(geo_type[4:]):
    #         API_geo = f"?geography={geo_type}"
    #     else:
    #         raise ValueError(f"`geo_type` value {geo_type} not valid")


    API_year = f"&date={year}-12"

    if dataset == "ECON_ACTIVE_STEM_PRO":
        fields = [
            "date",
            "date_name",
            "date_code",
            "geography_type",
            "geography_code",
            "measures_name",
            'variable',
            "cell_name",
            "obs_value",
            "obs_status_name",
            "obs_status",
            "record_count"
        ]

    else:
        fields = [
            "date",
            "date_name",
            "date_code",
            "geography_type",
            "geography_code",
            "measures_name",
            'variable',
            "variable_name",
            "obs_value",
            "obs_status_name",
            "obs_status",
            "record_count",
        ]

    API_select = f"&select={','.join(fields)}"
    column_map = {"GEOGRAPHY_NAME": "geo_nm", "GEOGRAPHY_CODE": "geo_cd"}

    query = API_start + API_geo + API_year + API_cols + API_select
    return query_nomis(query).rename(columns=column_map)


# def make_gva(project_dir, year):
#     """ Make and save dataset of GVA per capita
#
#     Args:
#         project_dir (str):
#             Path to project directory
#         year (int):
#             Year for which to use GVA estimate
#     """
#
#     gva_fin = f"{project_dir}/data/external/gva_pc.xls"
#     gva_fout = f"{project_dir}/data/interim/gva_pc.csv"
#
#     columns = {"LAU1 code": "lad_cd", "LA name": "lad_nm"}
#     df = (
#         read_excel(gva_fin, sheet_name="GVA per head", skiprows=2)
#         # Rename columns
#         .rename(columns=str)
#         .rename(columns=columns)
#         .pipe(
#             melt,
#             id_vars=["lad_cd", "lad_nm"],
#             value_vars=arange(1997, 2016).astype(str),
#             var_name="year",
#             value_name="gva_pc",
#         )
#     )
#
#     df.to_csv(gva_fout)


# def make_lad_ttwa_map(project_dir):
#     """ Make lookup between TTWA's and LAD's
#
#     Args:
#         project_dir (str, optional):
#             Path to project directory
#     """
#
#     if project_dir is None:
#         project_dir = beis_indicators.project_dir
#
#     nspl_fin = f"{project_dir}/data/raw/nspl.csv"
#     table_fout = f"{project_dir}/data/processed/lad_ttwa_lookup.csv"
#
#     # LOAD NSPL
#     nspl_cols = {"pcds": "postcode", "laua": "lad", "ttwa": "ttwa"}
#
#     nspl = read_csv(nspl_fin, usecols=nspl_cols.keys()).rename(columns=nspl_cols)
#
#     lookup_table = (  # Find overlap between TTWA and LAD
#         crosstab(nspl.ttwa, nspl.lad, normalize="index")
#         .reset_index(drop=False)
#         .pipe(melt, id_vars="ttwa")
#         .sort_values("ttwa")
#     )
#
#     lookup_table.to_csv(table_fout)


@ratelim.patient(REQUESTS_PER_SECOND, time_interval=1)
def query_nomis(link, offset_size=CELL_LIMIT):
    """ Query NOMIS api with ratelimiting and pagination

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

        if response.status_code == 200:

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

        else:
            continue

    # Concatenate all the outputs
    return concat(df_container)






def _check_geo_type_suffix(x):
    """ Checks if `geo_type` suffix contains an `int` """
    try:
        return int(x)
    except:
        raise ValueError(f"`geo_type` suffix: '{x}' cannot be parsed as `int`.")





if __name__ == "__main__":
    conf = beis_indicators.config["data"]["aps"]
    geo = ['nuts2010', 'nuts2013', 'nuts2016', 'lep']
    types = ['nuts', 'lep']

    years = conf["years"]

    for geo_type in types:
        make_nomis(geo_type, years, project_dir)



    # Test pivot
    # f_test = (
    #     f"{beis_indicators.project_dir}/data/processed/nomis_BRES_{years[0]}_{geo_type}.csv"
    # )
    # (
    #     read_csv(f_test).fillna(0)
    #     # Pivot to [areas x sectors]
    #     .pivot_table(
    #         index=["geo_cd", "geo_nm"],
    #         columns="cluster_name",
    #         values="value",
    #         fill_value=0,
    #         aggfunc="sum",
    #     )
    # )
