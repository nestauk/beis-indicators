from io import StringIO
import requests
import os
import logging

import ratelim
import pandas as pd
import re
from numpy import arange, sum
from pandas import concat, crosstab, melt, read_csv, read_excel
from beis_indicators import project_dir
from glob import glob
from dateutil.parser import parse
from datetime import datetime
from collections import defaultdict




import beis_indicators
from beis_indicators.utils.pandas import preview

conf = beis_indicators.config["data"]["aps"]

# geo_dict = {
#     'lep': conf["geography"]['lep'],
#     'nuts2':
#     {'2010': conf["geography"]['nuts2010']['nuts2'],'2013': conf["geography"]['nuts2013']['nuts2'], '2016': conf["geography"]['nuts2016']['nuts2']},
#     'nuts3':
#     {'2010': conf["geography"]['nuts2010']['nuts3'], '2013': conf["geography"]['nuts2013']['nuts3'], '2016': conf["geography"]['nuts2016']['nuts3']}
# }

geo_type = ['lep', 'nuts2', 'nuts3']


years = conf['years']

datasets = ["ECON_ACTIVE_STEM_PRO", "ECON_ACTIVE_NVQ_PRO", "STEM_DENSITY", "PRO_OCCS"]

dataset_columns = {
    'ECON_ACTIVE_NVQ_PRO': ['DATE', 'GEOGRAPHY_TYPE', 'geo_cd', 'OBS_VALUE'],
    'ECON_ACTIVE_STEM_PRO': ['DATE', 'GEOGRAPHY_TYPE', 'geo_cd', 'OBS_VALUE'],
    'STEM_DENSITY': ['DATE', 'GEOGRAPHY_TYPE', 'geo_cd', 'OBS_VALUE'],
    'PRO_OCCS': ['DATE', 'GEOGRAPHY_TYPE', 'geo_cd', 'OBS_VALUE']

}

geo_type_dict = {
    'nuts2' : ['nuts 2010 level 2', 'nuts 2013 level 2', 'nuts 2016 level 2'],
    'nuts3' : ['nuts 2010 level 3', 'nuts 2013 level 3', 'nuts 2016 level 3'],
    'lep' : ['local enterprise partnerships (as of April 2020)']

}

geo_codes = [beis_indicators.config["data"]["aps"]["geography"]["nuts2010"]["nuts2"],
    beis_indicators.config["data"]["aps"]["geography"]["nuts2010"]["nuts3"],
    beis_indicators.config["data"]["aps"]["geography"]["nuts2013"]["nuts2"],
    beis_indicators.config["data"]["aps"]["geography"]["nuts2013"]["nuts3"],
    beis_indicators.config["data"]["aps"]["geography"]["nuts2016"]["nuts2"],
    beis_indicators.config["data"]["aps"]["geography"]["nuts2016"]["nuts3"],
    beis_indicators.config["data"]["aps"]["geography"]["lep"]]

dates = {
 'nuts 2010 level 2': [i for i in range(2010,2012+1)],
 'nuts 2010 level 3': [i for i in range(2010,2012+1)],
 'nuts 2013 level 2' : [i for i in range(2013,2015+1)],
 'nuts 2013 level 3': [i for i in range(2013,2015+1)],
 'nuts 2016 level 2': [i for i in range(2016,2019+1)],
 'nuts 2016 level 3': [i for i in range(2016,2019+1)],
 'local enterprise partnerships (as of April 2020)': [i for i in range(2010,2019+1)]
}

def format_date(string):

    return datetime.strptime(string, '%Y-%m').year

def extract_year_from_string(string):
    match = re.search(r'\d{4}', string)
    return datetime.strptime(match.group(), '%Y').date().year
#
# def grab_geo(df):
#
#     for k,v in geo_type_dict.items():
#
#
#
#     return
#
# def clean_df(df):

cell_list_dict = {
    'stem_pro': 'T09a:7 (All people - Science, Research, Engineering and Technology Professionals (SOC2010) : All people )',
    'stem_assoc': 'T09a:19 (All people - Science, Engineering and Technology Associate Professionals (SOC2010) : All people )'

}

indicator_names = {

    'stem_pro': {'indicator': 'aps_econ_active_stem_profs_data', 'file': 'aps_econ_active_stem_profs_data'},
    'stem_assoc':{'indicator': 'aps_econ_active_stem_associate_profs_data', 'file': 'aps_econ_active_stem_associate_profs_data'}



}

indicator_names_1 = {
'nvq': {'indicator': 'aps_nvq4_education_data', 'file': 'aps_nvq4_education_data'},
'pro_occs':  {'indicator': 'aps_pro_occupations_data', 'file': 'aps_pro_occupations_data'},
'stem_dens': {'indicator': 'aps_econ_active_stem_density_data', 'file': 'aps_econ_active_stem_density_data'}
}

dataset_id_dict = {
    "ECON_ACTIVE_NVQ_PRO": 'nvq',
    "STEM_DENSITY": 'stem_dens',
    "PRO_OCCS":'pro_occs'
}

def split_df(df, dataset):
    if dataset == "ECON_ACTIVE_STEM_PRO":
        split_dfs = defaultdict(None)
        for k,v in cell_list_dict.items():

            df = df[df['CELL_NAME'] == v]
            split_dfs[k] = df
        return (split_dfs, type(split_dfs))

    else:
        return (df, type(df))




def make_indicators():

    for dataset in datasets:

        print(dataset)
        df_list = []

        chosen_cols = dataset_columns[dataset]

        path_string = f"{project_dir}/data/raw/aps/"
        files = glob('*path_string*')

        files = []
        for i in os.listdir(path_string):
            if os.path.isfile(os.path.join(path_string,i)) and dataset in i:
                files.append(i)

        # # print(files)
        # for file in files:
        #     # print(file)
        #     if os.path.exists(path_string + file):
        #         continue
        #     else:
        #         raise AttributeError(f"Run nomis_aps.py file to produce raw data files")


        for file in files:
            df = pd.read_csv(path_string + file)

            df_list.append(df)

        df_all = pd.concat(df_list)
        df_all['DATE'] = df_all['DATE'].apply(format_date)

        # df_all.to_csv(f"../../data/interim/aps/{dataset}_all.csv", index=False)

        for type in geo_type:

            # if geo_type_dict[type] in df_all['GEOGRAPHY_TYPE'].unique:
            #
            #
            type_df_list = []
            # print(type)
            for val in geo_type_dict[type]:
                df_part = df_all[(df_all['DATE'].isin(dates[val]))
                & (df_all['OBS_STATUS'] == 'A')
                & (df_all['GEOGRAPHY_TYPE'] == val)]
                # print(df_part.head(1))
                # print(df_part['MEASURES_NAME'].unique())

                if 'Value' in df_part['MEASURES_NAME'].unique():
                # if (dataset == "ECON_ACTIVE_STEM_PRO"):

                    df_part = df_part[(df_part['MEASURES_NAME'] =='Value')]
                    #& (df_part['CELL_NAME'] == '')]
                    type_df_list.append(df_part)

                elif 'Variable' in df_part['MEASURES_NAME'].unique():

                    df_part = df_part[(df_part['MEASURES_NAME'] =='Variable')]

                    type_df_list.append(df_part)







            df_all_type = pd.concat(type_df_list).reset_index(drop=True)
            # print(df_all_type['DATE'].unique())

            # print(df_all_type['CELL_NAME'].unique())

        #
            # print(df_all_type[df_all_type['CELL_NAME'] == cell_list_dict['stem_assoc']].head())
            # df_all_type = split_df(df_all_type, dataset)

            # print(df_all_type[0]['stem_assoc'].head(1))
            #
            # if df_all_type[1] == dict:
            #     df_all_type = df_all_type[0]

            if dataset == "ECON_ACTIVE_STEM_PRO":

                split_dfs = defaultdict(None)
                for k,v in cell_list_dict.items():
                    c = df_all_type[df_all_type['CELL_NAME'] == v]
                    split_dfs[k] = c
                split_dfs = dict(split_dfs)
                print(split_dfs['stem_pro']['DATE'].unique())

                for ind,df in split_dfs.items():

                    df_all_type = df

                    print(df_all_type.head(1))
                    df_value = df_all_type[chosen_cols]
                    # print(df_value.columns)

                    df_value.rename(columns = {"DATE": 'year', "OBS_VALUE": indicator_names[ind]['indicator']}, inplace=True)
                    df_value['year_spec'] = df_value['GEOGRAPHY_TYPE'].apply(extract_year_from_string)
                    del df_value['GEOGRAPHY_TYPE']
                    # print(df_value.columns)
                    if 'nuts' in type:
                        df_value.rename(columns = {"year_spec": 'nuts_year_spec', "geo_cd": 'nuts_id'}, inplace=True)
                        df_value = df_value[['year','nuts_id', 'nuts_year_spec', indicator_names[ind]['indicator']]].reset_index(drop=True)
                        df_value = df_value.sort_values(['nuts_id', 'year'])


                        df_value.to_csv(f"{project_dir}/data/processed/aps/{indicator_names[ind]['file']}.{type}.csv", index=False)


                    elif 'lep' in type:
                        df_value.rename(columns = {"year_spec": 'lep_year_spec', "geo_cd": 'lep_id'}, inplace=True)
                        df_value = df_value[['year','lep_id', 'lep_year_spec', indicator_names[ind]['indicator']]].reset_index(drop=True)
                        df_value = df_value.sort_values(['lep_id', 'year'])

                        df_value.to_csv(f"{project_dir}/data/processed/aps/{indicator_names[ind]['file']}.{type}.csv", index=False)

                    # else:
                    #     break


        #
        #
        #
        #
        #     #clean and save
        # #
            else:
                # df_all_type = df_all_type[0]
                if df_all_type.empty == False:
                    df_value = df_all_type[chosen_cols]
                    dataset_id = dataset_id_dict[dataset]
                    # for k,v in indicator_names_1.items():

                    df_value.rename(columns = {"DATE": 'year', "OBS_VALUE": indicator_names_1[dataset_id]['indicator']}, inplace=True)
                    df_value['year_spec'] = df_value['GEOGRAPHY_TYPE'].apply(extract_year_from_string)
                    del df_value['GEOGRAPHY_TYPE']

                    if 'nuts' in type:
                        df_value.rename(columns = {"year_spec": 'nuts_year_spec', "geo_cd": 'nuts_id'}, inplace=True)
                        df_value = df_value[['year','nuts_id', 'nuts_year_spec',  indicator_names_1[dataset_id]['indicator']]].reset_index(drop=True)
                        df_value = df_value.sort_values(['nuts_id', 'year'])

                        df_value.to_csv(f"{project_dir}/data/processed/aps/{ indicator_names_1[dataset_id]['file']}.{type}.csv", index =False)


                    elif 'lep' in type:
                        df_value.rename(columns = {"year_spec": 'lep_year_spec', "geo_cd": 'lep_id'}, inplace=True)
                        df_value = df_value[['year','lep_id', 'lep_year_spec',  indicator_names_1[dataset_id]['indicator']]].reset_index(drop=True)
                        df_value = df_value.sort_values(['lep_id', 'year'])

                        df_value.to_csv(f"{project_dir}/data/processed/aps/{ indicator_names_1[dataset_id]['file']}.{type}.csv", index =False)
        #         # else:
        #         #     break
        #
        # #
        # #         #clean and save

        #delete raw files

        # path_string = f"{project_dir}/data/raw/aps/"
        # files = glob('*file_string*')
        #
        # files = []
        # for i in os.listdir(path_string):
        #     if os.path.isfile(os.path.join(path_string,i)) and dataset in i:
        #         files.append(i)
        #
        # for file in files:
        #     # print(file)
        #     if os.path.exists(path_string + file):
        #         os.remove(path_string + file)
        #     else:
        #         continue



if __name__ == "__main__":

    make_indicators()
