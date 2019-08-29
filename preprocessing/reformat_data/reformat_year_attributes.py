# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 09:47:19 2019

@author: Florian Ulrich Jehn
"""
import os
import sys
import pandas as pd
# Get the location of this file
file_dir = os.path.dirname(os.path.abspath(__file__))


def read_df(name):
    os.chdir(os.path.abspath(os.path.join(file_dir, os.pardir+os.sep))+os.sep+"cleaned_data")
    df = pd.read_csv(name, sep=";", index_col=0)
    df.index = pd.to_datetime(df.index)
    return df

def add_water_year(df:pd.DataFrame):
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


def calc_yearly_means(df, data_type ,water_year=False):
    """Calculates the yearly mean in a df, either by normal or water year"""
    df = pd.DataFrame(df.mean(axis=1))
    df.columns=[data_type]
    add_water_year(df)
    grouper = "water_year" if water_year else df.index.year
    if "et" in data_type or "prec" in data_type:
        yearly_data = df.groupby(grouper).sum()
    else:
        yearly_data = df.groupby(grouper).mean()
    # Remove half empty years
    if water_year:
        yearly_data.drop(1991, inplace=True)
        yearly_data.drop(2019, inplace=True)
    return yearly_data.iloc[:,0]
    
    

if __name__ == "__main__":
    data_types = ["et_mm_1991_2018_corrected.csv", "prec_mm_1991_2018.csv", 
                  "soil_temp_C_1991_2018.csv"]
    dfs = {name:read_df(name) for name in data_types}
    yearly_means = []
    for data_type in dfs.keys():
        yearly_means.append(calc_yearly_means(dfs[data_type], data_type.split(".")[0], water_year=True))
        
    cleaned_year_attributes = pd.concat(yearly_means,axis=1)
    cleaned_year_attributes.to_csv("cleaned_year_attributes.csv", sep=";")
    
    

    
    
