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
                
                # Calculate the objective function to compare the real and the
                # simulated values. 
                y_sim = exponential(x, *optimal_parameters)
                obj_func = kge_non_parametric(y, y_sim)
                obj_func_all_catchments.loc[year,catch] = obj_func
        print("Finished: ")
        print(catch)

    return parameters_all_catchments, obj_func_all_catchments
            
        
def find_exponential_function(x,y):
    """ Finds the best parameter values for an exponential function"""
    optimal_parameters, pcov = curve_fit(exponential, x, y)
    return optimal_parameters
      

def _spearmann_corr(x, y):
    """
    Separmann correlation coefficient
    This is from the SPOTPY package:
        https://github.com/thouska/spotpy
    """
    col = [list(a) for a in zip(x, y)]
    xy = sorted(col, key=lambda x: x[0], reverse=False)
    # rang of x-value
    for i, row in enumerate(xy):
        row.append(i+1)

    a = sorted(xy, key=lambda x: x[1], reverse=False)
    # rang of y-value
    for i, row in enumerate(a):
        row.append(i+1)

    MW_rank_x = np.nanmean(np.array(a)[:,2])
    MW_rank_y = np.nanmean(np.array(a)[:,3])

    numerator = np.nansum([float((a[j][2]-MW_rank_x)*(a[j][3]-MW_rank_y)) for j in range(len(a))])
    denominator1 = np.sqrt(np.nansum([(a[j][2]-MW_rank_x)**2. for j in range(len(a))]))
    denominator2 = np.sqrt(np.nansum([(a[j][3]-MW_rank_x)**2. for j in range(len(a))]))
    return float(numerator/(denominator1*denominator2))


def kge_non_parametric(evaluation, simulation, return_all=False):
    """
    Non parametric Kling-Gupta Efficiency
    Corresponding paper:
    Pool, Vis, and Seibert, 2018 Evaluating model performance: towards a non-parametric variant of the Kling-Gupta efficiency, Hydrological Sciences Journal.
    output:
        kge: Kling-Gupta Efficiency
    
    author: Nadine Maier and Tobias Houska
    optional_output:
        cc: correlation 
        alpha: ratio of the standard deviation
        beta: ratio of the mean
    This code is from the SPOTPY package:
        https://github.com/thouska/spotpy
    """
    if len(evaluation) == len(simulation):
        ## self-made formula 
        cc = _spearmann_corr(evaluation, simulation)

        ### scipy-Version
        #cc = stm.spearmanr(evaluation, simulation, axis=0)[0]

        ### pandas version 
        #a  = pd.DataFrame({'eva': evaluation, 'sim': simulation})
        #cc = a.ix[:,1].corr(a.ix[:,0], method = 'spearman')

        fdc_sim = np.sort(simulation / (np.nanmean(simulation)*len(simulation)))
        fdc_obs = np.sort(evaluation / (np.nanmean(evaluation)*len(evaluation)))
        alpha = 1 - 0.5 * np.nanmean(np.abs(fdc_sim - fdc_obs))
 
        beta = np.mean(simulation) / np.mean(evaluation)
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
    import preprocessing.reformat_data.et_correction as et_cor
    in_dfs = ccdt.get_table_dict(calc_water_year=True)
    dataframes = {}
    for catch in list(in_dfs.keys())[:]:
        # Skip catchments with much missing or stepwise data
        if catch in [23950104, 24781159, 24781206, 428832990, 42870057]:
            print("Skipped: " + str(catch))
            continue
        dataframes[catch] = in_dfs[catch]
    et_cor.correct_and_save_ET(dataframes)
    calculate_dS(dataframes)
    
    parameters_all_catchments, obj_func_all_catchments = find_all_exp(dataframes, water_year=True)
#    Remove empty year 1991
    obj_func_all_catchments.drop(obj_func_all_catchments.index[:1], inplace=True)
    obj_func_all_catchments.to_csv("obj_func_all_catchments.csv", sep=";")
    

       

