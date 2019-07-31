import pandas as pd
import os
home = os.path.dirname(__file__) + '/cleaned_data'

def get_table_dict():
    """
    Loads the csv data and return a dict with catchment id as key and a dataframe as value
    """

    matQ = pd.read_csv(home + '/dis_mm_1991_2018.csv', delimiter=';', parse_dates=[0], index_col=0)
    matE = pd.read_csv(home + '/et_mm_1991_2018.csv', delimiter=';', parse_dates=[0], index_col=0)
    matP = pd.read_csv(home + '/prec_mm_1991_2018.csv', delimiter=';', parse_dates=[0], index_col=0)


    dataframes = {}

    for catch in matQ.columns:
        df = pd.DataFrame()
        df['Q'] = matQ[catch]
        df['E'] = matE[catch]
        df['P'] = matP[catch]
        dataframes[int(catch)] = df

    return dataframes

def get_attributes():

    return pd.read_csv(home + '/cleaned_attributes.csv', delimiter=';')