import pandas as pd
import os
home = os.path.dirname(__file__) 

def get_table_dict(calc_water_year=False):
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
        if calc_water_year:
            water_year(df)
        dataframes[int(catch)] = df

    return dataframes


def water_year(df:pd.DataFrame):
    """
    Adds a column to a dataframe (with datetime index) with the hydrological year 
    and one with the day of the water year
    """
    df["water_year"] = (df.index + pd.DateOffset(months=2)).year
    days_water_year = []
    for i, (year, year_df) in enumerate(df.groupby("water_year")):
        if i == 0:
            days_of_last_year = 30 + 31 # November plus December
            days_water_year += list(range(1 + days_of_last_year, year_df.shape[0]+1 + days_of_last_year))
        else:
            days_water_year += list(range(1, year_df.shape[0]+1))
    df["day_of_water_year"] = days_water_year


def get_attributes():

    return pd.read_csv(home + '/cleaned_attributes.csv', delimiter=';', index_col=0)


if __name__ == "__main__":
    dataframes = get_table_dict(calc_water_year=True)