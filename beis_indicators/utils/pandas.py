"""
"""
import logging
from IPython.display import display
import pandas as pd
import beis_indicators

logger = logging.getLogger(__name__)


def _clean_strings(x):
    """ Simple column name cleaning

    Remove leading/trailing whitespace, convert to lowercase,
    and replace spaces with underscores.

    Args:
        x (pandas.DataFrame): DataFrame

    Returns:
        pandas.DataFrame
    """

    return x.str.lstrip().str.rstrip().str.lower().str.replace(" ", "_")


def preview(x, nrows=5, T=False):
    """ Print a preview of DataFrame and return input

    Args:
        x (pandas.DataFrame): DataFrame to preview
        nrows (int, optional): 
        T (bool, optional): Whether to print transposed

    Returns:
        pandas.DataFrame
            Original input
    """

    if nrows >= x.shape[0]:
        out = x
    else:
        out = pd.concat([x.head(nrows), x.tail(nrows)])

    if T:
        out = out.T

    display(out)
    print(f"Shape: {x.shape}")

    return x
