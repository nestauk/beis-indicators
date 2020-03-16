import os
# import sys
import logging

from pathlib import Path
import pickle
import click
import gensim
import swifter
import numpy as np
import pandas as pd
from collections import defaultdict

import mi_scotland
from mi_scotland.features.nlproc import *
from mi_scotland.models.build_queries import sim_words
from mi_scotland.features.process_text import process_abstracts
from mi_scotland.utils.data_transformation import match_keys, match_values, filter_documents

np.random.seed(mi_scotland.config['seed'])


@click.command()
@click.option('--input', type=str, prompt='Raw data', help='Path to raw data.')
@click.option('--text_column', type=str, prompt='Text column', help='Column name of the text field.')
@click.option('--data_name', type=str, prompt='Dataset', help='The dataset you\'re using.')
@click.option('--output', type=str, prompt='Output file', help='Path to output file.')
@click.option('--id_column', type=str, prompt='ID column', help='Column name of the ID field.')
@click.option('--filter_docs', type=bool, prompt='Filter documents', help='Choose if the documents will be filtered before use.')
def main(input, text_column, data_name, output, id_column, filter_docs):
    ROOT_DIR = Path(__file__).resolve().parents[1]
    print(ROOT_DIR)
    DATA_INPUT = os.path.join(ROOT_DIR, "data/raw/", input)
    # text_column = sys.argv[2]
    # data_name = sys.argv[3]
    OUTPUT_FILE = os.path.join(ROOT_DIR, "data/processed/", output)
    # id_column = sys.argv[5]
    SEED_LIST_PATH = os.path.join(ROOT_DIR, "data/aux/", "keyword-seed-list.csv")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a logging format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # create a file handler
    handler = logging.FileHandler(
        f"{os.path.join(ROOT_DIR, ''.join([data_name, '.log']))}"
    )
    handler.setFormatter(formatter)

    # add the file handler to the logger
    logger.addHandler(handler)

    # Process dataset
    df = pd.read_csv(DATA_INPUT)
    logger.info(f"Unfiltered data shape: {df.shape}")

    if filter_docs:
        data = filter_documents(df, id_column=id_column, text_column=text_column, perc=10)
    else:
        data = df.assign(text_len=lambda x: x[text_column].str.len()).dropna(subset=["text_len"])[[id_column, text_column]]

    logger.info(f"Filtered data shape: {data.shape}")

    # Process text
    data["proc_text"] = (
        data[text_column].swifter.allow_dask_on_strings().apply(process_abstracts)
    ).dropna()
    logger.info(f"Finished text processing, moving to ngrams")

    data["proc_text"] = build_ngrams(list(data["proc_text"]))
    data = data[[id_column, "proc_text"]]
    logger.info(f"Finished ngrams - data shape: {data.shape}")

    # Build queries
    proc_text = list(data["proc_text"])

    # Train w2v
    w2v = gensim.models.Word2Vec(proc_text, size=mi_scotland.config['models']['word2vec']['size'], window=mi_scotland.config['models']['word2vec']['window'], min_count=mi_scotland.config['models']['word2vec']['min_count'], iter=mi_scotland.config['models']['word2vec']['iter'])

    # Save w2v model
    w2v.save(f'../models/w2v_{data_name}.model')

    logger.info(f"Done training w2v model")
    # Match text with keywords
    terms = pd.read_csv(SEED_LIST_PATH)

    logger.info(f"Extending seed list of strategic priorities")
    # dict({Strategic Priority: tokens})
    d = defaultdict(list)
    for _, row in terms.iterrows():
        if row['Seed List'] in w2v.wv.vocab:
            d[row["Strategic priorities"]].extend(sim_words(w2v, row["Seed List"], 10))
            d[row["Strategic priorities"]].append(row["Seed List"])

    # Keep unique tokens
    logger.info(f"Keep unique tokens.")
    d = {k: set(v) for k, v in d.items()}

    # Find emerging tech keywords for every ID
    logger.info(f"Match keywords and Strategic Priorities with IDs")
    data["keywords"] = data.proc_text.swifter.apply(match_values, d=d)
    # Add Strategic priorities
    data["Strategic Priority"] = data.keywords.swifter.apply(match_keys, d=d)

    logger.info("Saving data...")
    data.to_csv(OUTPUT_FILE, index=False)
    logger.info("Done :)")


if __name__ == "__main__":
    main()
