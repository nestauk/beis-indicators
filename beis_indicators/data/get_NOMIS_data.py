# This contains a set of classes, functions and utilities for the analysis of official data
import ratelim
import pandas as pd
from numpy import inf
from pathlib import Path


class QueryNomis():
    '''
    This class queries the Nomis API. It takes an API link extracted from the Nomis interface
    and the total number of records (which is used for pagination)

    '''

    def __init__(self, link, limit=None):
        '''
        Initialise with links and the total number of records

        '''

        self.link = link
        self.limit = inf if limit is None else limit

    #We use this decorator to be nice to the API
    @ratelim.patient(10,time_interval=5)
    def query_nomis(self):
        '''
        This method queries nomis for the data in the API.
        We keep things simple by using the pandas read_csv function directly

        '''

        #Link
        link = self.link

        self.total_records = None

        #DF container
        df_container =[]

        #Counters
        offset = 0
        records_left = 1  # dummy


        #While the final record we will obtain is below the total number of records:
        while(records_left>0):
            #Modify the query link with the offset
            query_link = link+'&recordoffset={off}'.format(off=str(offset))

            #Run query
            output = pd.read_csv(query_link)

            #Append output to our container list
            df_container.append(output)

            #Update the offset (next time we will query from this point)
            offset += 25000

            if self.total_records is None:
                self.total_records = output.RECORD_COUNT.values[0]
                records_left = self.total_records

            print(records_left)
            #This is the number of records left to collect
            records_left -= 25000

        #Concatenate all the outputs
        final_df = pd.concat(df_container)

        #Get it out
        return final_df

def _main(data_path):
    # 141: UK Business Counts - local units by industry and employment size band (2010 to 2017)
    # 142: UK Business Counts - enterprises by industry and employment size band (2010 to 2017)
    # 199: UK Business Counts - enterprises by industry and turnover size band (2010 to 2017)
    IDBR_ids = [141]
    
    # 172: Business Register and Employment Survey : open access (2015 to 2016)
    # 173: Business Register and Employment Survey public/private sector: open access (2015 to 2016)
    # 189: Business Register and Employment Survey (excluding units registered for PAYE only) : open access (2009 to 2015)
    # 190: Business Register and Employment Survey (excluding units registered for PAYE only) public/private sector : open access (2009 to 2015)
    BRES_ids = [172, 189]

    def API_start(data_id):
        return f"http://www.nomisweb.co.uk/api/v01/dataset/NM_{data_id}_1.data.csv"

    # LAD, TTWA geography queries of API
    API_lad = "?geography=TYPE464"
    API_ttwa = "?geography=TYPE447"

    # 4 digit SIC
    with open(f'{data_path}/aux/NOMIS_industry_4SIC_codes.txt') as f:
        codes = f.read().rstrip('\n')
    API_4SIC = f"&industry={codes}"

    ## BRES data
    # Select (employment by count) and set of columns to return
    API_BRES_cols = "&employment_status=4&measure=1&measures=20100&select=date_name,geography_type,geography_name,geography_code,industry_name,obs_value,obs_status_name,record_count"

    ## IDBR data
    # Select (employment by count) and set of columns to return
    API_IDBR_cols = "&employment_sizeband=0&legal_status=0&measures=20100&select=date_name,geography_type,geography_name,geography_code,industry_name,obs_value,obs_status_name,record_count"

    def rename_cols(df):
        return df.rename(columns={'GEOGRAPHY_NAME': 'geo_nm', 'GEOGRAPHY_CODE': 'geo_cd'})

    for data_id in IDBR_ids:
        # LAD
        dfi = QueryNomis(API_start(data_id)+API_lad+API_4SIC+API_IDBR_cols).query_nomis().pipe(rename_cols)
        dfi.to_csv(f'{data_path}/external/IDBR_LAD_{data_id}.csv')
        # TTWA
        # dfi = QueryNomis(API_start(data_id)+API_ttwa+API_4SIC+API_IDBR_cols+"&date=2016,2017").query_nomis().pipe(rename_cols)
        dfi = QueryNomis(API_start(data_id)+API_ttwa+API_4SIC+API_IDBR_cols).query_nomis().pipe(rename_cols)
        dfi.to_csv(f'{data_path}/external/IDBR_TTWA_{data_id}.csv')

    for data_id in BRES_ids:
        # LAD
        dfi = QueryNomis(API_start(data_id)+API_lad+API_4SIC+API_BRES_cols).query_nomis().pipe(rename_cols)
        dfi.to_csv(f'{data_path}/external/BRES_LAD_{data_id}.csv')
        # TTWA
        dfi = QueryNomis(API_start(data_id)+API_ttwa+API_4SIC+API_BRES_cols).query_nomis().pipe(rename_cols)
        dfi.to_csv(f'{data_path}/external/BRES_TTWA_{data_id}.csv')

if __name__ == '__main__':
    project_dir = Path(__file__).resolve().parents[2]
    data_path = project_dir / 'data'

    _main(data_path)
