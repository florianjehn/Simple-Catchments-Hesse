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
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))
import matplotlib.cm as cm
import math
from scipy.optimize import curve_fit



def plot_Q_vs_cumdS_scatter(dataframes, water_year=False):
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
            c = list(year_df.loc[year_df["P"]==0,:].month_of_water_year) if water_year else list(year_df.loc[year_df["P"]==0,:].index.month)
            year_df["cdS"] = np.cumsum(year_df["dS"])
            cdS = year_df.loc[year_df["P"] == 0, "cdS"]
            Q = year_df.loc[year_df["P"] == 0,"Q"]
            sc = plt.scatter(cdS, Q, c=c, cmap="coolwarm", edgecolors ="black", linewidths =0.2)
            plt.title("catchment: " + str(catch) + ", year: " + str(year)+" (no rain)")
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
            
def plot_Q_vs_cumdS_line(dataframes, water_year=False):
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
#            c = list(year_df.loc[year_df["P"]==0,:].month_of_water_year) if water_year else list(year_df.loc[year_df["P"]==0,:].index.month)
            year_df["cdS"] = np.cumsum(year_df.loc[:,"dS"])
            month_df = year_df.groupby("month_of_water_year" if water_year else year_df.index.month).mean()
            ax = plt.gca()
            c = np.linspace(0,1,11)
            for month in month_df.index[:-1]:
                Q_1 = month_df.loc[month, "Q"]
                cdS_1 = month_df.loc[month, "cdS"]
                Q_2 = month_df.loc[month+1, "Q"]
                cdS_2 = month_df.loc[month+1, "cdS"]             
                ax.plot([cdS_1, cdS_2],[Q_1, Q_2], color=cm.get_cmap("coolwarm")(c[month-1]), marker="o")

            plt.title("catchment: " + str(catch) + ", year: " + str(year)+" (with rain)")
            plt.xlabel("cum dS")
            plt.ylabel("Q")

            plt.savefig(str(catch) + "_" + str(year) + ".png")
            plt.close()
            
               
def find_all_exp(dataframes:dict, water_year=False):        
    """
    Finds the parameters for the function y = c * e ** (k * x) for all catchments
    and how much the values for the catchments differ from this function in every
    year
    """
    parameters_all_catchments = pd.DataFrame(columns=list(dataframes.keys()), index=[year for year in range(1991, 2019)])
    least_squares_all_catchments = pd.DataFrame(columns=list(dataframes.keys()), index=[year for year in range(1991, 2019)])
    for catch in dataframes.keys():
        df = dataframes[catch]
        grouped_years = df.groupby("water_year") if water_year else df.groupby(df.index.year)
        for year, year_df in grouped_years:
            if water_year:    
                # Skip half empty water years
                if year == 1991 or year == 2019:
                    continue
                # Calculate cummulative storage change
                year_df["cdS"] = np.cumsum(year_df.loc[:,"dS"])
                # Only use days without rain
                year_df = year_df[year_df["P"] == 0]
                # Check for nan
                if year_df.isnull().any().any():
                    print("\nhas nan")
                    print(catch)
                    print(year)
                    continue
                # Find the parameters
                x = normalize(year_df["cdS"])
                y = normalize(year_df["Q"])
                try:
                    optimal_parameters = find_exponential_function(x,y)
                except RuntimeError as err:
                    print("\n")
                    print(catch)
                    print(year)
                    print(err)
                    continue
                parameters_all_catchments.loc[year,catch] = optimal_parameters
                
                # Find the least sqaure difference from the polynomial and the
                # real data
                y_sim = exponential(x, *optimal_parameters)
                least_squares = calc_least_squares(y, y_sim)
                mean_least_squares = least_squares/len(y)
                least_squares_all_catchments.loc[year,catch] = mean_least_squares
        print("Finished: ")
        print(catch)

    return parameters_all_catchments, least_squares_all_catchments
  
def determine_simple_complex(least_squares_all_catchments):
    """ Determines if a catchment is complex or simple, based on how good
    its datapoints fit the exponential function. For all catchment considered
    the median value for the mean least squares is  0.011456798341574162"""
    type_simple_complex = pd.DataFrame(columns=least_squares_all_catchments.columns, index=least_squares_all_catchments.index)
    for catch in least_squares_all_catchments.columns:
        for year in least_squares_all_catchments.index:
            if least_squares_all_catchments.loc[year, catch] > 0.011456798341574162:
                type_simple_complex.loc[year, catch] = 2 # complex
            elif least_squares_all_catchments.loc[year, catch] < 0.011456798341574162: 
                type_simple_complex.loc[year, catch] = 1 # simple
            else:
                type_simple_complex.loc[year, catch] = np.nan
    type_simple_complex = type_simple_complex[type_simple_complex.columns].astype(float)
    return type_simple_complex
            
    
              
        
def find_exponential_function(x,y):
    """ Finds the best parameter values for an exponential function"""
    optimal_parameters, pcov = curve_fit(exponential, x, y)
    return optimal_parameters
      
def calc_least_squares(real, sim):
    dif = real - sim
    dif = dif ** 2
    return dif.sum()         

def exponential(x,c, k):
    """
    Exponential Funktion
    """
    return c*math.e**(k*x)

def calculate_dS(dataframes:dict):
    """
    Calculates the storage change for every day and adds it to the dataframes
    """
    for catch in dataframes.keys():
        df = dataframes[catch]
        df["dS"] = df.P - df.E_cor - df.Q
        
        

def normalize(series:pd.Series):
    return ((series - series.min()) / (series.max() - series.min()))  
        


if __name__ == '__main__':

    import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
    import preprocessing.reformat_data.et_correction as et_cor
    in_dfs = ccdt.get_table_dict(calc_water_year=True)
    dataframes = {}
    for catch in list(in_dfs.keys())[:]:
        # Skip catchments with much missing or stepwise data
        if catch in [23950104, 24781159, 24781206, 428832990]:
            print("Skipped: " + str(catch))
            continue
        dataframes[catch] = in_dfs[catch]
 #   attribs = ccdt.get_attributes()
    et_cor.correct_and_save_ET(dataframes)
    calculate_dS(dataframes)
    
    parameters_all_catchments, least_squares_all_catchments = find_all_exp(dataframes, water_year=True)
  #  extreme_areas = calculate_extreme_areas(dataframes, water_year=True)
 #   percentiles_flood, percentiles_delay = find_percentiles(extreme_areas)
 #   type_of_catchment = determine_class(extreme_areas, percentiles_flood, percentiles_delay, 0.8)
    
    #plot_Q_vs_cumdS(dataframes, water_year=True)
   # plot_Q_vs_cumdS_line(dataframes, water_year=True)
   # plt.close()
   # type_of_catchment = define_catchment_type_with_sum_ds(dataframes, water_year=True, monthly=True)
  #  type_of_catchment_float = type_of_catchment[type_of_catchment.columns].astype(float)
    
   # sns.heatmap(type_of_catchment_float, square=True, cmap="coolwarm", cbar=False, annot=True)    
       

#type_of_catchment = type_of_catchment[type_of_catchment.columns].astype(float)  # or int