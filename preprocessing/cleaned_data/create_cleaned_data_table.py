import pandas as pd
import os
home = os.path.dirname(__file__) 

def get_table_dict(calc_water_year=False, et_corrected=False):
    """
    Loads the csv data and return a dict with catchment id as key and a dataframe as value
    """
    
    matQ = pd.read_csv(home + os.sep + 'dis_mm_1991_2018.csv', delimiter=';', parse_dates=[0], index_col=0)
    matE = pd.read_csv(home + os.sep + 'et_mm_1991_2018_uncorrected.csv', delimiter=';', parse_dates=[0], index_col=0)
    matP = pd.read_csv(home + os.sep + 'prec_mm_1991_2018.csv', delimiter=';', parse_dates=[0], index_col=0)


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
    , hydrological day and hydrological month
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
    def shift_month(month):
        if month == 11:
            return 1
        elif month == 12:
            return 2
        else:
            return month + 2
    df["month_of_water_year"] = list(map(shift_month, list(df.index.month)))


def get_attributes_catchments_cat():

    return pd.read_csv(home + os.sep + 'cleaned_catchment_attributes_cat.csv', delimiter=';', index_col=0)

def get_attributes_catchments_num():
    attributes = pd.read_csv(home + os.sep + 'cleaned_catchment_attributes_num.csv', delimiter=';', index_col=0)
    attributes["dominating_soil_type_bk500"] = attributes["dominating_soil_type_bk500"].str.replace(" ", "")
    return attributes

def get_attributes_years():

    return pd.read_csv(home + os.sep + 'cleaned_year_attributes.csv', delimiter=';', index_col=0)

if __name__ == "__main__":
    dataframes = get_table_dict(calc_water_year=True)