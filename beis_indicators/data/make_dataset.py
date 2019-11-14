# -*- coding: utf-8 -*-
import logging
import os

import click
import requests
from dotenv import find_dotenv, load_dotenv

import beis_indicators
from beis_indicators import nomis

logger = logging.getLogger("beis_indicators")


@click.command()
@click.option("--first-time/--not-first-time", default=False)
def main(first_time):
    """ Runs data processing scripts.

    Turn raw data into cleaned data ready to be analyzed.

    Usage: `python make_dataset.py -e True`

    Args:
        external (bool, optional): If True, force download of external files
    """

    config = beis_indicators.config["data"]
    project_dir = beis_indicators.project_dir

    if first_time:
        pass

    # External
    ext_urls = config["external"]
    if not first_time:
        ext_files = os.listdir(f"{project_dir}/data/external/")
        not_found = [file_ for file_ in ext_urls.keys() if file_ not in ext_files]
        if not_found:
            msg = f"{not_found} not found, redownloading external files"
            logger.warning(msg)
            external = True
        else:
            external = False
            logger.info("All external files present")

    if first_time or external:
        for f_out, url in ext_urls.items():
            logger.info(f"Downloading {url}")
            r = requests.get(url)
            with open(f"{project_dir}/data/external/{f_out}", "wb") as f:
                f.write(r.content)

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
