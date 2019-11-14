import logging

import numpy as np
import pandas as pd
import scipy.stats as ss
from scipy.linalg import eig

import beis_indicators

logger = logging.getLogger(__name__)
np.seterr(all="raise")  # Raise errors on floating point errors


def create_lq(X, threshold=1, binary=False):
    """ Calculate the location quotient.

    Divides the share of activity in a location by the share of activity in
    the UK total.

    Args:
        X (pandas.DataFrame): Rows are locations, columns are sectors,
        threshold (float, optional): Binarisation threshold.
        binary (bool, optional): If True, binarise matrix at `threshold`.
            and values are activity in a given sector at a location.

    Returns:
        pandas.DataFrame

    #UTILS
    """

    Xm = X.values
    with np.errstate(invalid="ignore"):  # Accounted for divide by zero
        X = pd.DataFrame(
            (Xm * Xm.sum()) / (Xm.sum(1)[:, np.newaxis] * Xm.sum(0)),
            index=X.index,
            columns=X.columns,
        ).fillna(0)

    return (X > threshold).astype(float) if binary else X


def calc_fitness(X, n_iters):
    """ Calculate the fitness metric of economic complexity

    Args:
        X (pandas.DataFrame): Rows are locations, columns are sectors,
            and values are activity in a given sector at a location.
        n_iters (int): Number of iterations to calculate fitness for

    Returns:
        pandas.DataFrame

    #UTILS
    """

    X = _drop_zero_rows_cols(X)
    x = np.ones(X.shape[0])

    for n in range(1, n_iters):
        x = (X.values / (X.values / x[:, np.newaxis]).sum(0)).sum(1)
        x = x / x.mean()

    return pd.DataFrame(np.log(x), index=X.index, columns=["fitness"])


def calc_fit_plus(X, n_iters, correction=True):
    """ Calculate the fitness+ (ECI+) metric of economic complexity

    Args:
        X (pandas.Dataframe): Rows are locations, columns are sectors,
            and values are activity in a given sector at a location.
        n_iters (int): Number of iterations to calculate fitness for
        correction (bool, optional): If true, apply logarithmic correction.

    Returns:
        pandas.Dataframe

    #UTILS
    """

    X = _drop_zero_rows_cols(X)

    if X.dtypes[0] == bool:
        norm_mean = np.mean
    else:
        norm_mean = ss.gmean
    x = X.values.sum(axis=1)
    x = x / norm_mean(x)

    for n in range(1, n_iters):
        x = (X.values / (X.values / x[:, np.newaxis]).sum(0)).sum(1)
        x = x / norm_mean(x)

    if correction:
        x = np.log(x) - np.log((X / X.sum(0)).sum(1))
    else:
        pass  # x = np.log(x)

    return pd.DataFrame(x, index=X.index, columns=["fit_p"])


def calc_eci(X, sign_correction=True):
    """ Calculate the original economic complexity index (ECI).

    Args:
        X (pandas.DataFrame): Rows are locations, columns are sectors,
            and values are activity in a given sector at a location.
        sign_correction (bool, optional): If True, correct for the
            sign error that can occur using the eigenvector method

    Returns:
        pandas.DataFrame

    #UTILS
    """

    X = _drop_zero_rows_cols(X)

    C = np.diag(1 / X.sum(1))  # Diagonal entries k_C
    P = np.diag(1 / X.sum(0))  # Diagonal entries k_P
    H = C @ X.values @ P @ X.T.values
    w, v = eig(H, left=False, right=True)

    eci = pd.DataFrame(v[:, 1].real, index=X.index, columns=["eci"]).sort_values(
        "eci", ascending=False
    )
    sign = 1
    if sign_correction:
        # Flip sign if top 10th percentile has fewer entries than the bottom
        n_10pc = max(1, int(eci.shape[0] * 0.1))
        top_10_idx = eci.head(n_10pc).index
        bot_10_idx = eci.tail(n_10pc).index
        sign = 2 * (X.loc[top_10_idx].values.sum() < X.loc[bot_10_idx].values.sum()) - 1
        if sign == -1:
            logger.info("Corrected sign")

    return eci.loc[X.index] * sign


def _drop_zero_rows_cols(X):
    """ Drop regions/entities with no activity

    Fully zero column/row means ECI cannot be calculated
    """

    nz_rows = X.sum(1) > 0
    has_zero_rows = nz_rows.sum() != X.shape[0]
    if has_zero_rows:
        logger.warning(f"Dropping all zero rows: {X.loc[~nz_rows].index.values}")
        X = X.loc[nz_rows]
    nz_cols = X.sum(0) > 0
    has_zero_cols = nz_cols.sum() != X.shape[1]
    if has_zero_cols:
        logger.warning(f"Dropping all zero cols: {X.loc[:, ~nz_cols].columns.values}")
        X = X.loc[:, nz_cols]

    return X


def simple_diversity(X):
    """ Generate two simple measures of diversity

    The first measure is the number of areas engaging in an activity
    The second measure is the number of areas with a revealed comparative advantage

    Args:
        X (pandas.DataFrame): Rows are locations, columns are sectors,
            and values are activity in a given sector at a location.

    Returns:
        pandas.DataFrame

    #UTILS
    """

    div_1 = X.pipe(lambda x: np.sum(x > 0, axis=1)).to_frame("div_n_active")
    div_2 = (
        X.pipe(create_lq, binary=True, threshold=1).sum(axis=1).to_frame("div_n_RCA")
    )
    return pd.concat([div_1, div_2], axis=1)
