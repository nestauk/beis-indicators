import os
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from data_getters.patstat import select_patstat

load_dotenv(find_dotenv())
CONFIG = os.getenv("CONFIG")


def get_patstat(
    person_ctry_code="GB", earliest_filing_year=2010, database="patstat_2019_05_13"
):
    """Data getter wrapper to get patent data from our database.

    Args:
        person_ctry_code (:obj:`str`): Country code of the patent applicant.
        earliest_filing_year (:obj:`int`): Year of the earliest patent to retrieve.
        database (:obj:`str`): Database name.

    Returns:
        (:obj:`dict` of :obj:`pd.DataFrame`) PATSTAT tables.

    """
    return select_patstat(
        CONFIG,
        person_ctry_code=person_ctry_code,
        earliest_filing_year=earliest_filing_year,
        database=database,
    )


def prepare_patstat(dfs):
    """Get patent application IDs and patent descriptions that are written in English

    Args:
        dfs (:obj:`dict` of :obj:`pd.DataFrame`) PATSTAT tables.

    Return:
        (:obj:`pd.DataFrame`)

    """
    return dfs["appln_abstr"][dfs["appln_abstr"].appln_abstract_lg == "en"]
