# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 12:31:01 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
import os
import sys

# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))


def overview_plot(catchments, years):
    """
    Plots all catchment and year attributes in one big figure to give an 
    overview of all catchments
    """
    fig = plt.figure(figsize=(10,40))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[16,9], hspace=0.5)
    
    catchments_grid = gridspec.GridSpecFromSubplotSpec(4,4, subplot_spec=outer[0], wspace=0.5, hspace=1)
    
    years_grid = gridspec.GridSpecFromSubplotSpec(2,4, subplot_spec=outer[1], wspace=0.5, hspace=1)
    
    for i, attribute in enumerate(catchments.columns):
        current_att = catchments[attribute]
        ax = plt.Subplot(fig, catchments_grid[i])
        if current_att.dtypes != float:
            current_att = catchments.groupby(attribute)[attribute].count()

            print(current_att)
            current_att.plot.bar(ax=ax, stacked=True)
            for tick in ax.get_xticklabels():
                tick.set_rotation(45)
        else:
            current_att.plot.hist(ax=ax,histtype ="step", bins=15)
        ax.set_title(attribute)
        fig.add_subplot(ax)

        
    for j, attribute in enumerate(years.columns):
        ax = plt.Subplot(fig, years_grid[j])
        years[attribute].plot.hist(ax=ax,histtype ="step", bins=15)
        ax.set_title(attribute)

        fig.add_subplot(ax)
        
   # fig.tight_layout()
    fig.suptitle("\n\n\nCatchment Attributes\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nYear Attributes", 
                 horizontalalignment='center', color="red")

    fig.show()
    
    

if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments_num()
   catchments.drop("gauge", axis=1, inplace=True)

   years = ccdt.get_attributes_years()
   years.drop(['soil_temp_C_1991_2018', 'mean_air_temperature'], axis=1, inplace=True)
   overview_plot(catchments, years)