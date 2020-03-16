import gensim
import numpy as np
import mi_scotland

np.random.seed(mi_scotland.config['seed'])


def sim_words(w2v, token, topn=50):
    """Query a word2vec model with words and return a list of similar terms.

    Args:
        w2v: Pre-trained word vectors model.
        token (:obj:`str`): Token to query word2vec with.
        topn (:obj:`int`): Number of most similar tokens to return.

    Return
        (:obj:`list` of :obj:`str`)

    """
    return [tup[0] for tup in w2v.wv.most_similar([token], topn=topn)]
