# BEIS Indicators Data Collection and Processing

This directory contains the indicator data and the scripts required to make them.

To create a `conda` environment for collecting and processing data to create the indicators,
you can run:

```
make create_environment
```

To create a simpler deployment and documentation environment, simply use the `requirements.txt` file:

```
pip install -r requirements.txt
```

## Creating Indicators

Let's say you have some dataframe, `data`, with some values of pollution data (`pm10`) spanning different years (`year`) with x (`x`) and y (`y`) coordinates with EPSG projection 27700 that you want to aggregate to NUTS 2, NUTS 3 and LEP regions. The reverse geocoding, indicator aggregation and saving can be done for all region types in a few easy steps:


```python
import numpy as np
import pandas as pd
from beis_indicators.geo import NutsCoder
from beis_indicators.indicators import points_to_indicators

data = pd.read_csv('../path/to/data.csv')

# this may take a moment, especially if you have not downloaded the shapefiles
coders = {
    'nuts2': NutsCoder(level=2),
    'nuts3': NutsCoder(level=3),
    'lep': LepCoder()
    }

pollution = load_pollution_data(year, raw_data_dir, pollution_type)

for geo, coder in coders.items():
    mean_pm10 = points_to_indicator(data, value_col='pm10', coder=coder,
                    aggfunc=np.mean, value_rename='mean_pm10',
                    projection='EPSG:27700', x_col='x', y_col='y')
    save_indicator(mean_pm10, 'defra', geo)

```

## Organisation of this section

```
ds
├── Makefile           <- Makefile with commands like `make data` or `make dvc`
├── README.md          <- The README for the analysis
├── data
│   ├── README.md
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   ├── aux            <- Non-automatable human interventions, e.g. hand selected record ID's to ignore
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default Sphinx project; see sphinx-doc.org for details
│
├── logging.yaml       <- Logging config
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── model_config.yaml  <- Model configuration parameters
│
├── notebooks          <- Jupyter notebooks. Notebooks at the top level should have a markdown header
│   │                     outlining the notebook and should avoid function calls in favour of factored out code.
│   ├── notebook_preamble.ipy
│   │
│   └── dev            <- Development notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `_` delimited description, e.g.
│                         `01_jmg_eda.ipynb`.
│
├── pipe               <- Contains DVC pipeline files
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.py           <- makes project pip installable (pip install -e .) so beis_indicators can be imported
│
├── beis_indicators                <- Source code for use in this project.
│   ├── __init__.py    <- Makes beis_indicators a Python module
│   │
│   ├── data           <- Scripts to download or generate data
│   │   └── make_dataset.py
│   │
│   ├── features       <- Scripts to turn raw data into features for modeling
│   │   └── build_features.py
│   │
│   ├── models         <- Scripts to train models and then use trained models to make
│   │   │                 predictions
│   │   ├── predict_model.py
│   │   └── train_model.py
│   │
│   └── visualization  <- Scripts to create exploratory and results oriented visualizations
│       └── visualize.py
│
└── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io
```

<p><small>Project based on the <a target="_blank" href="https://github.com/nestauk/cookiecutter-data-science-nesta">Nesta cookiecutter data science project template</a>.</small></p>
