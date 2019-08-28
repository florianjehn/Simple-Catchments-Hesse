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


if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   attributes = ccdt.get_attributes()
   type_catchment = pd.read_csv("type_simple_complex.csv", index_col=0)
   variability_year = calculate_categorical_variability(type_catchment)
   variability_catch = calculate_categorical_variability(type_catchment, axis=1)
   
