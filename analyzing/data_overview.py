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
    fig = plt.figure(figsize=(20,30))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[16,9], hspace=0.15)
    
    catchments_grid = gridspec.GridSpecFromSubplotSpec(4,4, subplot_spec=outer[0], wspace=0.2, hspace=0.45)
    
    years_grid = gridspec.GridSpecFromSubplotSpec(2,4, subplot_spec=outer[1], wspace=0.2, hspace=0.2)
    
    axes = []
    for i, attribute in enumerate(catchments.columns):
        current_att = catchments[attribute]
        ax = plt.Subplot(fig, catchments_grid[i])
        if current_att.dtypes != float:
            current_att = catchments.groupby(attribute)[attribute].count()
            if attribute == "Permeability [/]":
                current_att.reindex(["very low", "low/very low", "low",
                                     "moderate/low", "moderate", "mid/moderate",
                                     "mid", "variable"]).plot.bar(ax=ax, 
                                        facecolor="lightsteelblue", 
                                        edgecolor="grey", linewidth=1,
                                        zorder=5)

            else:
                current_att.plot.bar(ax=ax,facecolor="lightsteelblue", 
                                        edgecolor="grey", linewidth=1,zorder=5)
            for tick in ax.get_xticklabels():
                tick.set_rotation(50)
            ax.set_xlabel("")
            ax.set_ylabel("Frequency")
        else:
            current_att.plot.hist(ax=ax,zorder=5,
                                  facecolor="lightsteelblue", 
                                        edgecolor="grey", linewidth=1,)
        ax.set_xlabel(attribute, alpha=0.7)
        fig.add_subplot(ax)
        axes.append(ax)

        
    for j, attribute in enumerate(years.columns):
        ax = plt.Subplot(fig, years_grid[j])
        years[attribute].plot.hist(ax=ax,  zorder=5,facecolor="lightsteelblue", 
                                        edgecolor="grey", linewidth=1)
        ax.set_xlabel(attribute, alpha=0.7)

        fig.add_subplot(ax)
        axes.append(ax)
    
    for ax in axes:
        # Make it nice
        plt.setp(ax.get_yticklabels(), alpha=0.7)
        plt.setp(ax.get_xticklabels(), alpha=0.7)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.yaxis.grid(True, color="lightgrey",zorder=0)
        ax.set_ylabel(ax.get_ylabel(), alpha=0.7)

    plt.savefig("overview.png", dpi=100, bbox_inches="tight")
    plt.close()
    
    

if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments()

   years = ccdt.get_attributes_years()
   years.drop(['soil_temp_C_1991_2018', 'mean_air_temperature'], axis=1, inplace=True)
   overview_plot(catchments, years)