# -*- coding: utf-8 -*-
"""
Created on Fri Aug 02 13:13:19 2019

@author: Florian Ulrich Jehn
"""
import os
import sys
import pandas as pd
import numpy as np
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))
import math
from scipy.optimize import curve_fit

               
def find_all_exp(dataframes:dict, water_year=True):        
    """
    Finds the parameters for the function y = c * e ** (k * x) for all catchments
    and how much the values for the catchments differ from this function in every
    year
    """
    parameters_all_catchments = pd.DataFrame(columns=list(dataframes.keys()), index=[year for year in range(1991, 2019)])
    obj_func_all_catchments = pd.DataFrame(columns=list(dataframes.keys()), index=[year for year in range(1991, 2019)])
    for catch in dataframes.keys():
        df = dataframes[catch]
        if water_year:
            grouped_years = df.groupby("water_year")
        else:
            grouped_years = df.groupby(df.index.year)
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
            
            # Calculate the objective function to compare the real and the
            # simulated values. 
            y_sim = exponential(x, *optimal_parameters)
            obj_func = kge(y, y_sim)
            obj_func_all_catchments.loc[year,catch] = obj_func
        print("Finished: ")
        print(catch)

    return parameters_all_catchments, obj_func_all_catchments
            
        
def find_exponential_function(x,y):
    """ Finds the best parameter values for an exponential function"""
    optimal_parameters, pcov = curve_fit(exponential, x, y)
    return optimal_parameters
      

def kge(evaluation, simulation, return_all=False):
    """
    Kling-Gupta Efficiency
    Corresponding paper: 
    Gupta, Kling, Yilmaz, Martinez, 2009, Decomposition of the mean squared error and NSE performance criteria: Implications for improving hydrological modelling
    output:
        kge: Kling-Gupta Efficiency
    optional_output:
        cc: correlation 
        alpha: ratio of the standard deviation
        beta: ratio of the mean
        
    THIS FUNCTION IS FROM THE SPOTPY PACKAGE
    https://github.com/thouska/spotpy/blob/master/spotpy/objectivefunctions.py
    """
    if len(evaluation) == len(simulation):
        cc = np.corrcoef(evaluation, simulation)[0, 1]
        alpha = np.std(simulation) / np.std(evaluation)
        beta = np.sum(simulation) / np.sum(evaluation)
        kge = 1 - np.sqrt((cc - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)
        if return_all:
            return kge, cc, alpha, beta
        else:
            return kge
    else:
        print("evaluation and simulation lists does not have the same length.")
        return np.nan

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
    in_dfs = ccdt.get_table_dict(calc_water_year=True)
    dataframes = {}
    for catch in list(in_dfs.keys())[:]:
        # Skip catchments with much missing or stepwise data
        if catch in [23950104, 24781159, 24781206, 428832990, 42870057, 23960709]:
            print("Skipped: " + str(catch))
            continue
        dataframes[catch] = in_dfs[catch]
    
    parameters_all_catchments, obj_func_all_catchments = find_all_exp(dataframes, water_year=True)
#    Remove empty year 1991
    obj_func_all_catchments.drop(obj_func_all_catchments.index[:1], inplace=True)
    obj_func_all_catchments.to_csv("obj_func_all_catchments.csv", sep=";")
    

       

