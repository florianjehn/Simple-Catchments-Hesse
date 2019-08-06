# -*- coding: utf-8 -*-
"""
Created on Fri Aug 02 13:13:19 2019

@author: Florian Ulrich Jehn
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_Q_vs_cumdS(dataframes, water_year=False):
    """
    Plots Q vs cumdS for seperated by year and river
    """
    import matplotlib
    matplotlib.use('Agg')
    for catch in dataframes.keys():
        df = dataframes[catch]
        grouped_years = df.groupby("water_year") if water_year else df.groupby(df.index.year)
        for year, year_df in grouped_years:
            # Skip half empty water years
            if water_year and (year == 1991 or year == 2019):
                continue
            c = list(year_df.month_of_water_year) if water_year else list(year_df.index.month)
            sc = plt.scatter(np.cumsum(year_df.dS), year_df.Q, c=c, cmap="coolwarm", edgecolors ="black", linewidths =0.2)
            plt.title("catchment: " + str(catch) + ", year: " + str(year))
            plt.xlabel("cum dS")
            plt.ylabel("Q")
            try:
                plt.legend(*sc.legend_elements())
            except ValueError as val:
                print(catch)
                print(year)
                print(val)
            #cbar = plt.colorbar(sc)
           # cbar.ax.set_ylabel('month', rotation=270)
            plt.savefig(str(catch) + "_" + str(year) + ".png")
            plt.close()
            
        
            

def create_polyfit(x: pd.Series, y: pd.Series):
    """
    Creates a polynomial function  for a bunch of values and returns a functions for it
    """
    fit = np.polyfit(x, y, deg=2)
    fit_function = np.poly1d(fit)
    return fit_function
    

def calculate_dS(dataframes:dict):
    """
    Calculates the storage change for every day and adds it to the dataframes
    """
    for catch in dataframes.keys():
        df = dataframes[catch]
        df["dS"] = df.P - df.E_cor - df.Q
        
        
def define_catchment_type(dataframes:dict, water_year=False):
    """
    Determines if a year of catchment belongs to a quick, slow or simpel type
    by splitting each year in half. The first half is used to create a regression.
    Then it is calculated how far the points of the second half are away from 
    this regression line. If they are mainly above, it is a quick catchment.
    If it is mainly below, it is a slow catchment. If it is somewhere in between
    it is a simple catchment. 
    """
    type_of_catchment = pd.DataFrame(columns=list(dataframes.keys()), index=[year for year in range(1991, 2019)])
    for catch in dataframes.keys():
        print(catch)
        df = dataframes[catch]
        grouped_years = df.groupby("water_year") if water_year else df.groupby(df.index.year)
        for year, year_df in grouped_years:
            if water_year:    
                # Skip half empty water years
                if year == 1991 or year == 2019:
                    continue
                first_half_of_year = year_df.loc[year_df.month_of_water_year.isin([1,2,3,5,6])]
                second_half_of_year = year_df.loc[year_df.month_of_water_year.isin([7,8,9,10,11,12])]
            else:
                first_half_of_year = year_df.loc[year_df.index.month.isin([1,2,3,5,6])]
                second_half_of_year = year_df.loc[year_df.index.month.isin([7,8,9,10,11,12])]
            try:
                # Create a polynomial from the first half of the year
                fit_function = create_polyfit(np.cumsum(first_half_of_year.dS), first_half_of_year.Q)
                # Create a fitted Q for the second half of the year
                fitted_Q = list(map(fit_function, np.cumsum(second_half_of_year.dS)))
                # Substract the values 
                mean_dif = np.mean(second_half_of_year.Q - fitted_Q)
                # Normalize by median
                mean_dif_norm = mean_dif / year_df.Q.mean()
                type_of_catchment.loc[year, catch] = mean_dif_norm
            except np.linalg.LinAlgError as er:
                print(catch)
                print(year)
                print(er)
                type_of_catchment.loc[year, catch] = np.nan
    return type_of_catchment


if __name__ == '__main__':
    # add the whole package to the path
    file_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))
    import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
    import preprocessing.reformat_data.et_correction as et_cor
    dataframes = ccdt.get_table_dict(calc_water_year=True)
    attribs = ccdt.get_attributes()
    et_cor.correct_and_save_ET(dataframes)
    calculate_dS(dataframes)
  #  plot_Q_vs_cumdS(dataframes, water_year=True)
    type_of_catchment = define_catchment_type(dataframes, water_year=True)
    type_of_catchment = type_of_catchment[type_of_catchment.columns].astype(float)
    sns.heatmap(type_of_catchment, square=True)
    
       

#type_of_catchment = type_of_catchment[type_of_catchment.columns].astype(float)  # or int