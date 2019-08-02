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

def plot_Q_vs_cumdS(dataframes):
    """
    Plots Q vs cumdS for seperated by year and river
    """
    for catch in dataframes.keys():
        df = dataframes[catch]
        for year, year_df in df.groupby(df.index.year):
            sc = plt.scatter(np.cumsum(year_df.dS), year_df.Q, c=list(year_df.index.dayofyear))
            plt.title("catchment: " + str(catch) + ", year: " + str(year))
            plt.xlabel("cum dS")
            plt.ylabel("Q")
            cbar = plt.colorbar(sc)
            cbar.ax.set_ylabel('day of year', rotation=270)
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
        
        
def define_catchment_type(dataframes:dict):
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
        for year, year_df in df.groupby(df.index.year):
            # Skip nan
            if year_df.isnull().values.any():
                continue
         #   print(year_df.index.months)
            jan_jun = year_df.loc[year_df.index.month.isin([1,2,3,5,6])]
            jul_dec = year_df.loc[year_df.index.month.isin([7,8,9,10,11,12])]
            # Create a polynomial from the first half of the year
            fit_function = create_polyfit(np.cumsum(jan_jun.dS), jan_jun.Q)
            # Create a fitted Q for the second half of the year
            fitted_Q = list(map(fit_function, np.cumsum(jul_dec.dS)))
            # Substract the values 
            mean_dif = np.mean(jul_dec.Q - fitted_Q)
            # Normalize 
            mean_dif = mean_dif / year_df.Q.mean()
            type_of_catchment.loc[year, catch] = mean_dif
    return type_of_catchment


if __name__ == '__main__':
    # add the whole package to the path
    file_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))
    import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
    import preprocessing.reformat_data.et_correction as et_cor
    dataframes = ccdt.get_table_dict()
    attribs = ccdt.get_attributes()
    et_cor.correct_and_save_ET(dataframes)
    calculate_dS(dataframes)
   # plot_Q_vs_cumdS(dataframes)
    type_of_catchment = define_catchment_type(dataframes)

