"""
 This file calculates economic complexity index (ECI) and product complexity
 index (PCI) for NOMIS (BRES & IDBR) data.
"""
import logging
from itertools import product, starmap
from functools import partial

import pandas as pd

import beis_indicators
from beis_indicators.utils.pandas import preview
from beis_indicators.nomis import pivot_area_industry
from beis_indicators.estimators.complexity import create_lq, calc_eci

logger = logging.getLogger(__name__)


def make_nomis_complexity(project_dir=None):
    """ Build economic complexity measures
    """

    if project_dir is None:
        project_dir = beis_indicators.project_dir

    config = beis_indicators.config["data"]["nomis"]
    years = config["years"]
    geo_type = config["geography"].upper()

    logger.info(
        f"Calculating ECI&PCI for BRES and NOMIS. years: `{years}`, geo: `{geo_type}`"
    )
    fin_stub = f"{project_dir}/data/processed/nomis"
    eci_fout = f"{project_dir}/data/processed/nomis_ECI.csv"
    pci_fout = f"{project_dir}/data/processed/nomis_PCI.csv"

    # Cartesian product: year x datset x taxonomy
    params = list(
        product(
            [fin_stub], years, ["BRES", "IDBR"], [geo_type], ["SIC4", "cluster_name"]
        )
    )
    # ECI
    (pd.concat(starmap(_nomis_complexity, params)).pipe(preview).to_csv(eci_fout))
    # PCI
    (
        pd.concat(starmap(partial(_nomis_complexity, PCI=True), params))
        .pipe(preview)
        .to_csv(pci_fout)
    )

    return


def _nomis_complexity(fin_stub, year, dataset, geo_type, sector_col, PCI=False):
    """ Calculate complexity index for a given snapshot of NOMIS data

    Args:
        fin_stub (str): File-stub for input BRES dataset
        year (str): Year
        dataset (str, {'BRES', 'IDBR'}): NOMIS dataset
        geo_type (str): Type of regional geography
        sector_col (str): Name of sector column to use to pivot on
        PCI (bool, optional): If True, calculate product complexity by
            transposing input

    Returns:
        pandas.DataFrame
    """
    return (
        pd.read_csv(f"{fin_stub}_{dataset}_{year}_{geo_type}.csv", index_col=0)
        .pipe(pivot_area_industry, sector_col)
        .pipe(create_lq, binary=True)
        .fillna(0)
        .pipe(lambda x: x.T if PCI else x)  # Transpose if PCI
        .pipe(calc_eci)
        .pipe(lambda x: x.rename(columns={"eci": "pci"}) if PCI else x)  # Rename if PCI
        .assign(year=year, geo_type=geo_type, source=dataset, sector_type=sector_col)
    )


if __name__ == "__main__":
    logger = logging.getLogger("complexity")
    make_nomis_complexity()
