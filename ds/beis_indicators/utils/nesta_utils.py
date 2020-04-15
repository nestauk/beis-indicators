import pandas as pd

def get_daps_data(table,connection,chunksize=1000):
    '''
    Utility function to get data from DAPS with less faff
    
    Args:
        -table is the SQL table in DAPS that we are extracting
        -connection is the database connection we are using
        -Chunksize are the chunks to download
    
    Returns:
        -A dataframe with the data we have collected
    
    '''
    #Get chunks
    chunks = pd.read_sql_table(table, connection, chunksize=chunksize)
    
    #Create df
    df = pd.concat(chunks)
    
    #Return data
    return(df)