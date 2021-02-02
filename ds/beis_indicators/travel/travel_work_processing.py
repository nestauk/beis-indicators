import numpy as np
import pandas as pd
import io
import urllib.request
import requests
import camelot
from beis_indicators import project_dir

def download_data():

    travel_to_work_2016 = 'https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/adhocs/007252averagehometoworktraveltimeages16andoverocttodec2016/2017update.xls'
    travel_to_work_2017 = 'https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/adhocs/006022averagehometoworktraveltimeages16plusocttodec2015/2018updateod17data.xls'
    travel_to_work_2018 = 'https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/adhocs/010202averagehometoworktraveltimeage16yearsandoverukoctobertodecember2018/averagehometoworktraveltimes16plusod18.xls'


    resp_16 = requests.get(travel_to_work_2016)
    resp_17 = requests.get(travel_to_work_2017)
    resp_18 = requests.get(travel_to_work_2018)

    output_16 = open(f'{project_dir}/data/raw/travel/travel_to_work_2016.xls', 'wb')
    output_17 = open(f'{project_dir}/data/raw/travel/travel_to_work_2017.xls', 'wb')
    output_18 = open(f'{project_dir}/data/raw/travel/travel_to_work_2018.xls', 'wb')

    output_16.write(resp_16.content)
    output_17.write(resp_17.content)
    output_18.write(resp_18.content)
    output_16.close()
    output_17.close()
    output_18.close()

def load_updated_codes():

    file = "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/migrationwithintheuk/methodologies/interalmigrationmethodology/internalmigrationmethodology2016.pdf"
    tables = camelot.read_pdf(file, pages = "15-end")
    changes_1 = pd.concat([tables[0].df,tables[1].df]).iloc[1:]

    changes_1[0] = changes_1[0].apply(lambda x: x.replace('\n', ''))
    changes_1[1] = changes_1[1].apply(lambda x: x.replace('\n', ''))
    changes_1[2] = changes_1[2].apply(lambda x: x.replace('\n', ''))
    changes_1[3] = changes_1[3].apply(lambda x: x.replace('\n', ''))

    changes_2 = pd.concat([tables[2].df,tables[3].df]).drop([0,0])

    changes_2[0] = changes_2[0].apply(lambda x: x.replace('\n', ''))
    changes_2[1] = changes_2[1].apply(lambda x: x.replace('\n', ''))
    changes_2[2] = changes_2[2].apply(lambda x: x.replace('\n', ''))

    convert_dict = dict(zip(changes_1[2], changes_1[3]))

    return convert_dict.update(dict(zip(changes_2[1], changes_2[2])))

def get_travel_work_data():

    download_data()

    xl_16 = pd.ExcelFile(f'{project_dir}/data/raw/travel/travel_to_work_2016.xls')
    xl_17 = pd.ExcelFile(f'{project_dir}/data/raw/travel/travel_to_work_2017.xls')
    xl_18 = pd.ExcelFile(f'{project_dir}/data/raw/travel/travel_to_work_2018.xls')

    df_16 = xl_16.parse('OD16').drop('Office For National Statistics', axis=1)
    df_17 = xl_17.parse('OD17').drop('Office For National Statistics', axis=1)
    df_18 = xl_18.parse('OD18').drop('Office For National Statistics', axis=1)

    df_16.columns = ['UALADGB UA / LAD of residence', 'Mean']
    df_17.columns = ['UALADGB UA / LAD of residence', 'Mean']
    df_18.columns = ['UALADGB UA / LAD of residence', 'Mean']

    df_16 = df_16[9:419].reset_index(drop=True)
    df_17 = df_17[9:419].reset_index(drop=True)
    df_18 = df_18[9:419].reset_index(drop=True)

    # print(df_16.head())

    df_16['Code'] = df_16['UALADGB UA / LAD of residence'].apply(lambda x: x.strip().split(" ",1)[0])
    df_16['LAD'] = df_16['UALADGB UA / LAD of residence'].apply(lambda x: x.strip().split(" ",1)[1])

    df_17['Code'] = df_17['UALADGB UA / LAD of residence'].apply(lambda x: x.strip().split(" ",1)[0])
    df_17['LAD'] = df_17['UALADGB UA / LAD of residence'].apply(lambda x: x.strip().split(" ",1)[1])

    df_18['Code'] = df_18['UALADGB UA / LAD of residence'].apply(lambda x: x.strip().split(" ",1)[0])
    df_18['LAD'] = df_18['UALADGB UA / LAD of residence'].apply(lambda x: x.strip().split(" ",1)[1])

    del df_16['UALADGB UA / LAD of residence']
    del df_17['UALADGB UA / LAD of residence']
    del df_18['UALADGB UA / LAD of residence']

    df_16['Code'] = df_16['Code'].apply(lambda x: ('00'+ x) if len(x) <= 2 else x)
    df_17['Code'] = df_17['Code'].apply(lambda x: ('00'+ x) if len(x) <= 2 else x)
    df_18['Code'] = df_18['Code'].apply(lambda x: ('00'+ x) if len(x) <= 2 else x)

    equivs = pd.read_csv(f'{project_dir}/data/aux/equivalents_regions.csv',encoding='cp1252')
    equiv_df = equivs[equivs.GEOGCDO.isin(df_16['Code'].tolist())][['GEOGCD','GEOGCDO', 'STATUS']]
    equiv_df.columns = ['GEOGCD', 'Code', 'Status']

    df_16 = df_16.merge(equiv_df, on='Code', how='left')
    df_17 = df_17.merge(equiv_df, on='Code', how='left')
    df_18 = df_18.merge(equiv_df, on='Code', how='left')

    df_16.drop_duplicates(subset='Code', inplace=True)
    df_17.drop_duplicates(subset='Code', inplace=True)
    df_18.drop_duplicates(subset='Code', inplace=True)

    df_16.reset_index(drop=True,inplace=True)
    df_17.reset_index(drop=True,inplace=True)
    df_18.reset_index(drop=True,inplace=True)

    convert_dict = load_updated_codes()

    df_16['GEOGCD'] = df_16['GEOGCD'].replace(convert_dict)
    df_17['GEOGCD'] = df_17['GEOGCD'].replace(convert_dict)
    df_18['GEOGCD'] = df_18['GEOGCD'].replace(convert_dict)

    df_16 = df_16[~df_16['Mean'].isna()]
    df_16['Mean'] = df_16['Mean'].astype(float)

    df_17 = df_17[~df_17['Mean'].isna()]
    df_17['Mean'] = df_17['Mean'].astype(float)

    df_18 = df_18[~df_18['Mean'].isna()]
    df_18['Mean'] = df_18['Mean'].astype(float)

    df_16 = df_16.groupby('GEOGCD').mean().reset_index()
    df_17 = df_17.groupby('GEOGCD').mean().reset_index()
    df_18 = df_18.groupby('GEOGCD').mean().reset_index()

    df_16['year'] = 2016
    df_17['year'] = 2017
    df_18['year'] = 2018

    lad_lat_lon = pd.read_csv(f'{project_dir}/data/raw/travel/Local_Authority_Districts__December_2016__Boundaries_UK.csv')

    lad_lat_lon.rename(columns={'lad16cd': 'GEOGCD'}, inplace = True)

    df_16_geo = df_16.merge(lad_lat_lon, on='GEOGCD', how='left').drop_duplicates(subset='GEOGCD').reset_index(drop=True)
    df_17_geo = df_17.merge(lad_lat_lon, on='GEOGCD', how='left').drop_duplicates(subset='GEOGCD').reset_index(drop=True)
    df_18_geo = df_18.merge(lad_lat_lon, on='GEOGCD', how='left').drop_duplicates(subset='GEOGCD').reset_index(drop=True)

    df_16_geo = df_16_geo[['Mean', 'year', 'long', 'lat']]
    df_17_geo = df_17_geo[['Mean', 'year', 'long', 'lat']]
    df_18_geo = df_18_geo[['Mean', 'year', 'long', 'lat']]

    df_geo = pd.concat([df_16_geo, df_17_geo, df_18_geo])

    df_geo.to_csv(f'{project_dir}/data/interim/travel_to_work_all_years.csv', index=False)

# if __name__ == "__main__":
#     get_travel_work_data()
