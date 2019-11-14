import numpy as np
import pandas as pd
from itertools import chain


def flatten_lists(lst):
    """Remove nested lists. #UTILS"""
    return list(chain(*lst))


def match_values(row, d):
    """Find the overlap of a dictionary's values with a set.

    Args:
        row (:obj:`list`): List of tokens.
        d (:obj:`dict`): Dictionary of the format {key technologies: [kw1, kw2 ..., kwN]}

    Returns:
        (:obj:`list` of :obj:`str`)

    #UTILS
    """
    lst = [set(row) & v for v in d.values() if len(set(row) & v) > 0]
    return list(chain(*lst))


def match_keys(row, d):
    """Find the overlap of a dictionary's keys with a set.

    Args:
        row (:obj:`list`): List of tokens.
        d (:obj:`dict`): Dictionary of the format {key technologies: [kw1, kw2 ..., kwN]}

    Returns:
        (:obj:`list` of :obj:`str`)

    #UTILS
    """
    return [k for k, v in d.items() if len(set(row) & v) > 0]


def _remove_short_docs(data, text_column, perc=10):
    """ Remove documents with a number of characters up to the 10th
        percentile of their distribution.

    Args:
        data (:obj:`pd.DataFrame`): Table to preprocess.
        text_column (:obj:`str`): Column name with text data that will be used in processing.

    Return:
        (:obj:`pd.DataFrame`)

    #UTILS
    """
    short_docs_len = np.percentile(data.text_len, perc)
    return data[data["text_len"] >= short_docs_len]


def filter_documents(data, id_column, text_column, perc):
    """Filter empty values and short documents from a DataFrame.

    Args:
        data (:obj:`pandas.DataFrame`): Pandas DataFrame with a text field.
        id_column (:obj:`str`): Column name with the text data to use.
        text_column (:obj:`str`): Column name with the text data to use.

    Returns:
        (:obj:`list` of :obj:`str`): List of documents.

    #UTILS
    """
    return (
        data.assign(text_len=lambda x: x[text_column].str.len())
        .dropna(subset=["text_len"])
        .drop_duplicates(text_column)
        .pipe(_remove_short_docs, text_column, perc)[[id_column, text_column]]
    )
