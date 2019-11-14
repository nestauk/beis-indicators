import numpy as np

import mi_scotland
from mi_scotland.features.nlproc import tokenize_document
from mi_scotland.utils.data_transformation import flatten_lists

np.random.seed(mi_scotland.config['seed'])


def process_abstracts(text):
    """Process text data.

    Args:
        text (:obj:`str`): Text data.

    Return:
        (:obj:`list` of :obj:`str`):

    """
    if isinstance(text, str):
        return flatten_lists(tokenize_document(text))
    else:
        np.nan
