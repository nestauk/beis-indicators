# -*- coding: utf-8 -*-
import logging
import os

import click
import requests
from dotenv import find_dotenv, load_dotenv

import beis_indicators
from beis_indicators import nomis

logger = logging.getLogger("beis_indicators")


def main():
    """ Runs data processing scripts.

    Turn raw data into cleaned data ready to be analyzed.

    Usage: `python make_dataset.py -e True`

    Args:
        external (bool, optional): If True, force download of external files
    """

    config = beis_indicators.config["data"]
    project_dir = beis_indicators.project_dir

    logger.info("Building nomis data")
    nomis_years = config["nomis"]["years"]
    nomis_geog = config["nomis"]["geography"].upper()
    nomis.make_nomis(geo_type=nomis_geog, year_l=nomis_years)
    nomis.make_nomis_complexity()


if __name__ == "__main__":
    load_dotenv(find_dotenv())

    try:
        msg = f"Making datasets"
        logger.info(msg)
        main()
    except (Exception, KeyboardInterrupt) as e:
        logger.exception(e, stack_info=True)
        raise e
