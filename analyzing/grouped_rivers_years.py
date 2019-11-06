# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 11:44:42 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import numpy as np
import scipy
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))


def create_color_lookup(unique_attributes):
    """
    Creates a lookup table for the different attributes
    """
    color_lookup = {}
    colors = sns.color_palette("terrain", len(unique_attributes))
    for att, color in zip(unique_attributes, colors):
        color_lookup[att] = color
    return color_lookup


def plot_differences_catchments_years_by_least_squares(least_squares, attributes, amount_homogen, year_catch):
    """
    Plots the difference in the catchments (axis=0) or year (axis=1) in 
    regard to the catchmetns with the highest/lowest median least square error
    """

    # Get the predominant type for every year/catchment
    if year_catch == "catch":
        mean_least_squares = least_squares.mean(axis=0)
    elif year_catch == "year":
        mean_least_squares = least_squares.mean(axis=1)
        
    # Find the year/catchment that have the highest and lowest least square error
    simple_catch_year = mean_least_squares[mean_least_squares < mean_least_squares.quantile(amount_homogen)].index.astype(float)
    complex_catch_year = mean_least_squares[mean_least_squares > mean_least_squares.quantile(1-amount_homogen)].index.astype(float)
    most_homogen = {"simple": simple_catch_year, "complex":complex_catch_year}
        
    # Create a figure for every attribute
    for att in attributes.columns:
        print(att)
        attributes_for_types = {}
        for type_catch in most_homogen.keys():
            homogen_type = most_homogen[type_catch]
            attributes_for_one_type = attributes.loc[homogen_type, att]
            attributes_for_one_type.name = type_catch
            attributes_for_one_type.reset_index(inplace=True, drop=True)
            attributes_for_types[type_catch] = attributes_for_one_type
     #       print(attributes_for_one_type)
            
        all_types = pd.concat([attributes_for_types[type_catch] for type_catch in attributes_for_types.keys()],axis=1)
        print(all_types)
   #     all_types.columns = 

        # if they are not flaot or int they should be categorical
        if attributes[att].dtypes != np.float64 and attributes[att].dtypes != np.int64:
            all_types_by_cat = pd.concat([all_types.groupby(col).count() for col in all_types.columns],axis=1)
            all_types_by_cat = all_types_by_cat[all_types_by_cat.columns[::-1]]
            ax = all_types_by_cat.transpose().plot(kind="bar", stacked=True)
            ax.set_title(year_catch + "; attribute: " + att+ "; n="+str(len(simple_catch_year)))

        else:
            ax = sns.swarmplot(data=all_types)
            ax = sns.boxplot(data=all_types, showcaps=False,boxprops={'facecolor':'None'},
        showfliers=False,whiskerprops={'linewidth':0})
      #      ax = all_types.plot(kind="box") 
       #     print(all_types)
            # Do a corrected t test to see if they are significantly different
            statistic, p_value = scipy.stats.ranksums(all_types["simple"], all_types["complex"])
#            bonferroni = 11 if year_catch == "year" else 15
#            p_value = p_value * bonferroni
            ax.set_title(year_catch + "; attribute: " + att + "; p_val: "+str(np.round(p_value,decimals=3)) + "; n="+str(len(simple_catch_year)))
            
            
        fig = plt.gcf()
        fig.tight_layout()
        plt.savefig(year_catch + "_attribute_" + att+ ".png", dpi=150,  bbox_inches="tight")
        plt.close()      
        
        
if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments_num()
   years = ccdt.get_attributes_years()
   least_squares = pd.read_csv("least_square_all_catchments.csv", sep=";", index_col=0)
   plot_differences_catchments_years_by_least_squares(least_squares, catchments , 0.2, "catch")
   plot_differences_catchments_years_by_least_squares(least_squares, years, 0.2, "year")
