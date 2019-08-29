# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 11:44:42 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import matplotlib as mpl
import matplotlib.patches as mpatches
import os
import sys
import math
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))


def measure_categorical_variability(categorical_data:list):
    """
    Calculates the measure of variability in categorical data based on the 
    paper "Two Simple Measures of Variability for Categorical Data"
    by Allaj (2017)
    """
    relative_frequencies = []
    categorical_data = [cat for cat in categorical_data if str(cat) != "nan"]
    for unique_cat in set(categorical_data):        
        frequencies = categorical_data.count(unique_cat)
        rel_freq = frequencies / len(categorical_data)
        relative_frequencies.append(rel_freq)
    relative_frequencies_squared = [val ** 2 for val in relative_frequencies]
    sum_relative_frequencies_root = math.sqrt(sum(relative_frequencies_squared))
    measure_of_variability = 1 - sum_relative_frequencies_root
    return measure_of_variability
    
    
def calculate_categorical_variability(df, axis=0):
    """
    Calculates the variability of a dataframe, either by row (axis=0) or 
    by column (axis=1)
    """
    if axis == 0:
        to_iter = df.index
    elif axis == 1:
        to_iter = df.columns
        df = df.transpose()
    results = pd.DataFrame(index=to_iter,columns=[0])
    for select in to_iter:
        measure_of_variability = measure_categorical_variability(list(df.loc[select]))
        results.loc[select,0] = measure_of_variability
    return results


def create_color_lookup(unique_attributes):
    """
    Creates a lookup table for the different attributes
    """
    color_lookup = {}
    colors = sns.color_palette("terrain", len(unique_attributes))
    for att, color in zip(unique_attributes, colors):
        color_lookup[att] = color
    return color_lookup


def plot_differences_catchments_years(type_catchment, attributes, variability, amount_homogen, year_catch):
    """
    Plots the difference in the catchments (axis=0) or year (axis=1) in 
    regard to the river behavior
    """
    mapping = {1.0:"simple", 2.0:"complex"}

    # Get the predominant type for every year/catchment
    if year_catch == "catch":
        mode = type_catchment.mode(axis=1).iloc[0,:]
    elif year_catch == "year":
        mode = type_catchment.mode(axis=1).iloc[:,0]

    # Find all the different types
    unique_catchment_types = pd.concat([pd.Series((type_catchment[col].unique())) for col in type_catchment.columns]).dropna().unique()
    
    # Find the year/catchment that have the mainly either complex or simple behavior
    most_homogen = {}
    for type_catch in unique_catchment_types:
        # Get only those types of the current type
        of_type = mode[mode==type_catch].index
        # Get the variability of those types
        variability_of_type = variability.loc[of_type]
        # get those with the lowest variability (e.g. catchments that are always complex)
        most_homogen[type_catch] = variability_of_type.sort_values(by=0).head(amount_homogen).index.astype(float)
        
    # Create a figure for every attribute
    for att in attributes.columns:
        attributes_for_types = {}
        for type_catch in unique_catchment_types:
            homogen_type = most_homogen[type_catch]
            attributes_for_one_type = attributes.loc[homogen_type, att]
            attributes_for_one_type.name = type_catch
            attributes_for_one_type.reset_index(inplace=True, drop=True)
            attributes_for_types[type_catch] = attributes_for_one_type
            
        all_types = pd.concat([attributes_for_types[type_catch] for type_catch in attributes_for_types.keys()],axis=1)
        all_types.columns = [mapping[col] for col in all_types.columns]

        # if they are not flaot they should be categorical
        if attributes[att].dtypes != float:
            all_types_by_cat = pd.concat([all_types.groupby(col).count() for col in all_types.columns],axis=1)
            ax = all_types_by_cat.transpose().plot(kind="bar", stacked=True)
        else:
            ax = all_types.plot(kind="box")            
            
        ax.set_title(year_catch + "; attribute: " + att)
        plt.savefig(year_catch + "_attribute_" + att + "_n_is_" + str(amount_homogen) + ".png", dpi=150)
        plt.close()      


if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments_num()
   for col in catchments.columns:
       try:
           catchments = catchments[catchments.columns].astype(float)
       except ValueError as err:
           pass
   years = ccdt.get_attributes_years()
   type_catchment = pd.read_csv("type_simple_complex.csv", index_col=0)
   
   variability_year = calculate_categorical_variability(type_catchment)
   variability_year = variability_year[variability_year.columns].astype(float)
   variability_catch = calculate_categorical_variability(type_catchment, axis=1)
   variability_catch = variability_catch[variability_catch.columns].astype(float)
   
   #plot_differences_catchments_years(type_catchment,catchments,  variability_catch, 10, "catch")
   plot_differences_catchments_years(type_catchment, years,  variability_year, 3, "year")
