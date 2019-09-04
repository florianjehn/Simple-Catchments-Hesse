# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 09:47:19 2019

@author: Florian Ulrich Jehn
"""
import os
import numpy as np
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
            days_water_year += list(range(1 + days_of_last_year, 
                                          year_df.shape[0]+1 + days_of_last_year))
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
    

def calc_yearly_attributes(df, water_year = False):
    """Calculates a bunch of attributes for the different years"""
    daily_means = prepare_data(df, water_year=water_year)
    grouper = "water_year" if water_year else df.index.year
    years = list(set(daily_means["water_year"].values)) if water_year else list(set(daily_means.index.year))
    grouped_years = daily_means.groupby(grouper)
    attributes = pd.DataFrame(index = years)
    attributes["longest_dry_spell"] = find_longest_dry_spell(grouped_years)
    attributes["dry_days"] = find_dry_days(grouped_years)
    attributes["longest_rain_period"] = find_longest_rain_period(grouped_years)
    attributes["rain_days"] = find_rain_days(grouped_years)
    attributes["most_rain_one_day"] = find_most_rain_one_day(grouped_years)
    attributes["most_rain_one_month"] = find_most_rain_one_month(grouped_years, water_year=water_year)
    attributes["least_rain_one_month"] = find_least_rain_one_month(grouped_years, water_year=water_year)
    attributes["rainfall_seasonality"] = calc_rainfall_seasonality(grouped_years, water_year=water_year)#
    air_temp = calculate_air_temperature()
    attributes["mean_air_temperature"] = calc_yearly_means(air_temp, "air_temp", water_year=water_year)
    attributes["days_with_snow"] = calc_snow_days(prec, air_temp, water_year)
    attributes["days_below_0_C"] = calc_freezing_days(air_temp, water_year)
    attributes["snow_fraction"] = calc_snow_fraction(prec,air_temp, water_year)

    print(attributes)
    return attributes
   
def calc_snow_days(prec,air_temp, water_year):
    """Calculates how many days below 0°C had precipitation"""
    prec = prepare_data(prec, water_year=water_year)
    air_temp = prepare_data(air_temp, water_year=water_year)
    combined = pd.concat([air_temp.iloc[:,0],prec.iloc[:,:2]],axis=1)
    combined.columns = ["air_temp", "prec", "water_year"]
    combined = combined[combined["air_temp"] < 0]
    combined = combined[combined["prec"] > 0]
    combined = combined.groupby("water_year").count()
    return combined.iloc[:,0]


def calc_freezing_days(air_temp,water_year):
    """Calculates how many days are below 0°C"""
    air_temp = prepare_data(air_temp, water_year=water_year)
    air_temp = air_temp[air_temp.iloc[:,0] < 0]
    return air_temp.groupby("water_year").count().iloc[:,0]

def calc_snow_fraction(prec, air_temp, water_year):
    """Calculates how much of the precipitation falls below 0°C"""
    prec = prepare_data(prec, water_year=water_year)
    air_temp = prepare_data(air_temp, water_year=water_year)
    combined = pd.concat([air_temp.iloc[:,0],prec.iloc[:,:2]],axis=1)
    combined.columns = ["air_temp", "prec", "water_year"]  
    all_prec = combined.groupby("water_year")["prec"].sum()
    below_0 = combined[combined["air_temp"] < 0].groupby("water_year")["prec"].sum()
    return below_0/all_prec
    
    


def find_longest_dry_spell(grouped_years):
    """Finds the longest dry spell for all years"""
    dryspell_by_year = {}
    for year, year_df in grouped_years:
        longest_dryspell_overall = 0
        longest_dryspell_current = 0
        yearly_prec = year_df.iloc[:,0]
        for day in yearly_prec.index:
            if yearly_prec.loc[day] == 0:
                longest_dryspell_current += 1
                if longest_dryspell_current > longest_dryspell_overall:
                    longest_dryspell_overall = longest_dryspell_current
            else:
                longest_dryspell_current = 0
        dryspell_by_year[year] = longest_dryspell_overall
    return pd.Series(dryspell_by_year)

def find_dry_days(grouped_years):
    """Counts how many dry days are happening in all the years"""
    dry_days_by_year = {}
    for year, year_df in grouped_years:
        yearly_prec = year_df.iloc[:,0]
        dry_days_by_year[year] = yearly_prec[yearly_prec == 0].count()
    return pd.Series(dry_days_by_year)


def find_longest_rain_period(grouped_years):
    """Finds the longest rain_period for all years"""
    rain_period_by_year = {}
    for year, year_df in grouped_years:
        longest_rain_period_overall = 0
        longest_rain_period_current = 0
        yearly_prec = year_df.iloc[:,0]
        for day in yearly_prec.index:
            if yearly_prec.loc[day] > 0:
                longest_rain_period_current += 1
                if longest_rain_period_current > longest_rain_period_overall:
                    longest_rain_period_overall = longest_rain_period_current
            else:
                longest_rain_period_current = 0
        rain_period_by_year[year] = longest_rain_period_overall
    return pd.Series(rain_period_by_year)


def find_rain_days(grouped_years):
    """Counts how many dry days are happening in all the years"""
    dry_days_by_year = {}
    for year, year_df in grouped_years:
        yearly_prec = year_df.iloc[:,0]
        dry_days_by_year[year] = yearly_prec[yearly_prec > 0].count()
    return pd.Series(dry_days_by_year)


def prepare_data(df, water_year=False):
    """Prepares the precipitation data, so it can be used more easily in other 
    functinos"""
    daily_means = pd.DataFrame(df.mean(axis=1))
    if water_year:
        add_water_year(daily_means)
        daily_means = daily_means[daily_means["water_year"] != 1991]
        daily_means = daily_means[daily_means["water_year"] != 2019]
    return daily_means



def find_most_rain_one_day(grouped_years):
    most_rain_one_day_by_year = {}
    for year, year_df in grouped_years:
        yearly_prec = year_df.iloc[:,0]
        most_rain_one_day_by_year[year] = yearly_prec.max()
    return pd.Series(most_rain_one_day_by_year)

def find_most_rain_one_month(grouped_years, water_year=False):
    most_rain_one_month_by_year = {}
    for year, year_df in grouped_years:
        grouper = "month_of_water_year" if water_year else year_df.index.month
        monthly_sum = year_df.groupby(grouper).sum()[0]
        most_rain_one_month_by_year[year] = monthly_sum.max()
    return pd.Series(most_rain_one_month_by_year)
        
def find_least_rain_one_month(grouped_years, water_year=False):
    least_rain_one_month_by_year = {}
    for year, year_df in grouped_years:
        grouper = "month_of_water_year" if water_year else year_df.index.month
        monthly_sum = year_df.groupby(grouper).sum()[0]
        least_rain_one_month_by_year[year] = monthly_sum.min()
    return pd.Series(least_rain_one_month_by_year)


def calc_rainfall_seasonality(grouped_years, water_year=False):
    """Calculates the seasonality index for rainfall as described in 
    Walsh, R. P. D., & Lawler, D. M. (1981). RAINFALL SEASONALITY:
        DESCRIPTION, SPATIAL PATTERNS AND CHANGE THROUGH TIME. 
        Weather, 36(7), 201–208. doi:10.1002/j.1477-8696.1981.tb05400.x 
    """
    rainfall_seasonality_by_year = {}
    for year, year_df in grouped_years:
        grouper = "month_of_water_year" if water_year else year_df.index.month
        yearly_sum = year_df.iloc[:,0].sum()
        monthly_sum = year_df.groupby(grouper).sum()[0]
        sum_monthly_derivation = 0
        for month in monthly_sum.index:
            sum_monthly_derivation += abs(monthly_sum[month] - (yearly_sum/12))
        seasonality_index = sum_monthly_derivation / yearly_sum
        rainfall_seasonality_by_year[year] = seasonality_index
    return pd.Series(rainfall_seasonality_by_year)
        

def calculate_air_temperature():
    """Calculates the air temperature, based on correlations between soil and
    air temperature
    """
    soil_temp_5_cm = pd.read_csv("soil_temp_C_1991_2018.csv", sep=";",index_col=0)
    #This function is based on correlations between soil and air temperature
     #for 5 stations where we have both data. """
    func = np.poly1d([6.923754321609094081e-06,
                     -5.028251353322844798e-04,
                     1.421928716424386042e-02,
                     -1.859218178888984996e-01,
                     1.837777166384310545e+00,
                     -3.650731052002345600e-01])
    air_temp = pd.DataFrame(func(soil_temp_5_cm), index=soil_temp_5_cm.index, 
                        columns = soil_temp_5_cm.columns)  
    for column in air_temp.columns:
        air_temp[column] = air_temp[column].astype(float)
    air_temp.index = pd.to_datetime(air_temp.index)
    return air_temp        
        

if __name__ == "__main__":
    data_types = ["et_mm_1991_2018_corrected.csv", "prec_mm_1991_2018.csv", 
                  "soil_temp_C_1991_2018.csv"]
    dfs = {name:read_df(name) for name in data_types}
    yearly_means = []
    for data_type in dfs.keys():
        yearly_means.append(calc_yearly_means(dfs[data_type], data_type.split(".")[0], water_year=True))
        
    cleaned_year_attributes = pd.concat(yearly_means,axis=1)
    prec = dfs["prec_mm_1991_2018.csv"]
    additional_attributes = calc_yearly_attributes(prec, water_year=True)
    cleaned_year_attributes= pd.concat([cleaned_year_attributes, additional_attributes],axis=1)

    
    
    cleaned_year_attributes.to_csv("cleaned_year_attributes.csv", sep=";")
    
    

    
    
