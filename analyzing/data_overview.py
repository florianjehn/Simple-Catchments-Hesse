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


def overview_plot(catchments):
    """
    Plots all catchment and year attributes in one big figure to give an 
    overview of all catchments
    """
    fig = plt.figure(figsize=(12.5 ,15))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2,3], hspace=0.4)
    
    cat_grid = gridspec.GridSpecFromSubplotSpec(2,3, subplot_spec=outer[0], wspace=0.3, hspace=1)
    cat_att = ['Land Use [/]', 'Soil Texture [/]', 'Soil Type [/]',
               'Aquifer Conductivity [/]', 'Geology Type [/]','Permeability [/]']
    
    num_grid = gridspec.GridSpecFromSubplotSpec(3,3, subplot_spec=outer[1], wspace=0.3, hspace=0.5)
    
    axes = []
    color_bars = "#529DCC"
    color_edges = "black"
    cat_count = 0
    num_count = 0
    for attribute in catchments.columns:
        current_att = catchments[attribute]
        if attribute in cat_att:    
            ax = plt.Subplot(fig, cat_grid[cat_count])
            cat_count += 1
        else:
            ax = plt.Subplot(fig, num_grid[num_count])
            num_count += 1            
        if current_att.dtypes != float:
            current_att = catchments.groupby(attribute)[attribute].count()
            if attribute == "Permeability [/]":
                current_att.reindex(["very low", "low/very low", "low",
                                     "moderate/low", "moderate", "mid/moderate",
                                     "mid", "variable"]).plot.bar(ax=ax, 
                                        facecolor=color_bars, 
                                        edgecolor=color_edges, linewidth=1,
                                        zorder=5)

            else:
                current_att.plot.bar(ax=ax,facecolor=color_bars, 
                                        edgecolor=color_edges, linewidth=1,zorder=5)
            # for tick in ax.get_xticklabels():
            #     tick.set_rotation(75)
            ax.set_xlabel("")
            ax.set_ylabel("Frequency")
        else:
            current_att.plot.hist(ax=ax,zorder=5,
                                  facecolor=color_bars, 
                                        edgecolor=color_edges, linewidth=1,)
        ax.set_title(attribute, alpha=0.7)
        fig.add_subplot(ax)
        axes.append(ax)

        

    
    for ax in axes:
        # Make it nice
        plt.setp(ax.get_yticklabels(), alpha=0.7)
        plt.setp(ax.get_xticklabels(), alpha=0.7)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        for i,spine in enumerate(ax.spines.values()):
            if i == 2:
                continue
            spine.set_visible(False)
        ax.yaxis.grid(True, color="lightgrey",zorder=0)
        ax.set_ylabel(ax.get_ylabel(), alpha=0.7)
        
        # Add suptitles for gridspec
    rect_top = 0.5, 0.9, 0, 0.0  # lower, left, width, height (I use a lower height than 1.0, to place the title more visible)
    rect_bottom = 0.5, 0.52, 0, 0
    ax_top = fig.add_axes(rect_top)
    ax_bottom = fig.add_axes(rect_bottom)
    ax_top.set_xticks([])
    ax_top.set_yticks([])
    ax_top.spines['right'].set_visible(False)
    ax_top.spines['top'].set_visible(False)
    ax_top.spines['bottom'].set_visible(False)
    ax_top.spines['left'].set_visible(False)
    ax_top.set_facecolor('none')
    ax_bottom.set_xticks([])
    ax_bottom.set_yticks([])
    ax_bottom.spines['right'].set_visible(False)
    ax_bottom.spines['top'].set_visible(False)
    ax_bottom.spines['bottom'].set_visible(False)
    ax_bottom.spines['left'].set_visible(False)
    ax_bottom.set_facecolor('none')
    ax_top.set_title('Categorical Attributes', fontsize=16, alpha=0.7)
    ax_bottom.set_title('Numerical Attributes', fontsize=16, alpha=0.7)    
    
    
    plt.savefig("overview.png", dpi=200, bbox_inches="tight")
    plt.close()
    
    

if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments()
   # Climate first
   catchments = catchments.reindex(['Act. Evapotranspiration [mm]', 'Discharge [mm]', 'Precipitation [mm]', 'Runoff-Ratio [/]',
                       # Land use
                       'Land Use [/]',
                       # topography
                        'Area [km²]',  'Elongation Ratio [/]','Slope [/]',
                        # Soils
                        'Soil Depth [m]','Soil Texture [/]','Soil Type [/]', 
                        # Groundwater
                        'Aquifer Conductivity [/]', 'Geology Type [/]', 'Ground Water Recharge [mm]',        'Permeability [/]'

        ], axis=1)

   overview_plot(catchments)