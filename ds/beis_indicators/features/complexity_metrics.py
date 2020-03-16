import numpy as np
import pandas as pd
import scipy.stats as ss
from scipy.linalg import eig

def preview(x):
    """preview pandas function"""
    print(x.shape)
    display(x.head())
    return x

def create_lq(X, binary=False):
    """ Calculate the location quotient.

    Divides the share of activity in a location by the share of activity in the UK total

    Args:
        X (pandas.DataFrame): DataFrame where rows are locations, columns are sectors and values are activity in a given sector at a location.
        binary (bool, optional): If True, discretise the data with a cut-off value of 1

    Returns:
        pandas.DataFrame
    """
    Xm = X.values
    X = pd.DataFrame((Xm/Xm.sum(1)[:, np.newaxis])/(Xm.sum(0)/Xm.sum()),
            index=X.index, columns=X.columns)
    
    return (X > 1) if binary else X

def calc_fitness(X, n_iters):
    """ Calculate the fitness metric of economic complexity

    Args:
        X (pandas.DataFrame): DataFrame where rows are locations, columns are sectors and values are some proxy of activity (e.g. RCA) in a given sector at a location.
        n_iters (int): Number of iterations to calculate fitness for

    Returns:
        pandas.DataFrame
    """
    x = np.ones(X.shape[0])

    for n in range(1, n_iters):
        x = (X.values/(X.values/x[:, np.newaxis]).sum(0)).sum(1)
        x = x/x.mean()

    return pd.DataFrame(np.log(x), index=X.index, columns=['fitness'])

def calc_fit_plus(X, n_iters, correction=True):
    """ calculate the fitness+ metric of economic complexity

    args:
        x (pandas.dataframe): dataframe where rows are locations, columns are sectors and values are some proxy of activity (e.g. rca) in a given sector at a location.
        n_iters (int): number of iterations to calculate fitness for
        correction (bool, optional): if true, apply logarithmic correction.

    returns:
        pandas.dataframe

    NOTE: See [REF] 
    """
    if X.dtypes[0] == bool:
        norm_mean = np.mean
    else:
        norm_mean = ss.gmean
    x = X.values.sum(axis=1)
    x = x/norm_mean(x)

    for n in range(1, n_iters):
        x = (X.values/(X.values/x[:, np.newaxis]).sum(0)).sum(1)
        x = x/norm_mean(x)

    if correction:
        x = np.log(x) - np.log((X/X.sum(0)).sum(1))
    else:
        pass# x = np.log(x)
    
    return pd.DataFrame(x, index=X.index, columns=['fit_p'])


def calc_ECI(X):
    """ Calculate the original economic complexity index (ECI).

    Args:
        X (pandas.DataFrame): DataFrame where rows are locations, columns are sectors and values are some proxy of activity (e.g. RCA) in a given sector at a location.

    Returns:
        pandas.DataFrame

    NOTE: Uses eigenvectors for the calculation which only guarantees correctness up to a sign.
    """

    C = np.diag(1/X.sum(1))  # Diagonal entries k_C
    P = np.diag(1/X.sum(0))  # Diagonal entries k_P
    H = C @ X @ P @ X.T
    w, v = eig(H, left=False, right=True)

    return pd.DataFrame(v[:, 1].real, index=X.index, columns=['eci'])


def simple_diversity(X, name):
    """
    Takes a dataframe (e.g. BRES or IDBR) and generates 2 simple measures of diversity 

    Args:
        X (pandas.DataFrame): DataFrame where rows are locations, columns are sectors and values are some proxy of activity (e.g. RCA) in a given sector at a location.
        name (str): Name of data input

    Returns:
        pandas.DataFrame
    """
    
    div_1 = X.apply(lambda x: np.sum(x > 0), axis=1)
    
    div_2 = create_lq(X).apply(lambda x: np.sum(x >1), axis=1)
    
    out = pd.concat([div_1, div_2], axis=1)
    out.columns = ['div_abs_'+name, 'div_esp_'+name]
    
    return out


def into_segment(X, segments):
    """
    Regroups the data into Nesta segments

    Args:
        X (pandas.DataFrame): DataFrame where rows are locations, columns are sectors and values are some proxy of activity (e.g. RCA) in a given sector at a location.
        name (str): Name of data input

    Returns:
        pandas.DataFrame

    NOTE: Need REF
    """
    
    X.columns = [x.strip() for x in X.columns]
    
    #We use the place variable for pivoting
    place_var = X.index.name
        
    segmented = pd.pivot_table(
            pd.merge(
                pd.melt(X.reset_index(drop=False),id_vars=place_var)
                ,segments, left_on='variable',right_on='sic'),
            index=place_var,columns='cluster',values='value',aggfunc='sum')
        
    return segmented


def pivot_area_industry(df, year=None):
    """Convert BRES/IDBR data to pivot table to analyse ECI
    
    Drops uneccessary columns
    Renames columns
    Extracts SIC numbers from full string
    (optional) filter by year
    Convert to pivot table with rows as regions and columns as SIC
    
    Args:
        df (pandas.DataFrame): Raw input data
        year (int, optional): Year to consider
        
    Returns:
        pandas.DataFrame: [number areas x number SIC]
        
    """
    # If no year is selected aggregate over years
    if year is None:
        aggfunc = np.mean
    else:
        aggfunc = np.sum

    if 'local' in df.iloc[0].GEOGRAPHY_TYPE:
        geog_type = 'LAD'
    elif 'travel' in df.iloc[0].GEOGRAPHY_TYPE:
        geog_type = 'TTWA'
    else:
        geog_type = 'region'
        
    return (
            (df
             # Drop un-needed cols
             .drop(['RECORD_COUNT', 'GEOGRAPHY_TYPE', 'OBS_STATUS_NAME'], axis=1)
             # Rename columns
             .rename(columns={'INDUSTRY_NAME': 'SIC4',
                              'OBS_VALUE': 'employment', 'DATE_NAME': 'year'})
             # Fill missing values with zeros
             .fillna(0)
             # Extract SIC number from full string name
             .assign(SIC4=lambda x: x.SIC4.str.extract('(.*):'))
             # Filter by `year`
             .pipe(lambda x: x.query(f'year == {year}') if year else x)
             # Pivot to [locations x sectors]
             .pivot_table(index='geo_cd', columns='SIC4', values='employment', fill_value=0, aggfunc=aggfunc)
            ),
            # Return geography name-code lookup
            pd.DataFrame(df.groupby(['geo_nm', 'geo_cd']).first().index.tolist(), columns=['geo_nm', 'geo_cd'])
           )

class ComplexityTransformer():
    """
    Initialised with a df of activity
    Methods:
    .eci: calculates eci
    .fit_plus: calculates eci+
    
    Attributes:
    .input_df
    .segmented_df
    .segments
    .eci (places)
    .fit_plus (places)
    .eci_i (industries)
    .fit_plus_i (industries)
    
    """
    
    def __init__(self, measures='all', segments=None, year=None,
            ECI_RCA=True, FIT_RCA=False, n_iters=200, correction=False):
        """
        Initialise an instance with a df and the segment lookup
        
        """

        if measures == 'all':
            self.measures = ['ECI', 'fit_plus']

        self.segments = segments
        self.year = year
        self.ECI_RCA = ECI_RCA
        self.FIT_RCA = FIT_RCA
        self.n_iters = n_iters
        self.correction = correction

    def transform(self, X, y=None):

        X, geo = pivot_area_industry(X, year=self.year)

        if self.segments is not None:
            X = into_segment(X, self.segments)

        return pd.merge(pd.concat([self.calc_eci(X), self.calc_fit_plus(X)], axis=1).reset_index(),
                geo.reset_index(drop=True), on='geo_cd')

    
    def calc_eci(self, X):
        """
        Make ECI.
        
        Args:
            Segmented = if we want to turn the data into Nesta segments
        
        Returns:
            Attributes with eci and industry eci. Segmented df if we did the segmentation
        
        """
        
        ECI = calc_ECI(create_lq(X, binary=self.ECI_RCA))
        # Correct sign of ECI under the assumption that complexity 
        # is positively associated with total size of a region
        corr = ECI.corrwith(X.sum(1)).values
        sign_correction = 1 if (corr > 0) else -1

        tmp = ECI.join(X.sum(1).to_frame('ttwa_size')).sort_values('eci')
        sign_correction = 1 if (tmp.head().ttwa_size.mean() < tmp.tail().ttwa_size.mean()) else -1

        print('sign_correction', sign_correction)
#         if sign_correction == -1:
#             import pdb
#             pdb.set_trace()

        return ECI * sign_correction
        
        
    def calc_fit_plus(self, X):
        """
        Make ECI+
        
        Args:
            Segmented (if we want to segment)
        
        Returns:
            Attributes with ECI+. Segmented df if we did segmentation
        
        """
        
        return calc_fit_plus(X, n_iters=self.n_iters, correction=self.correction)
