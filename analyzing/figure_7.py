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
from matplotlib import gridspec
import matplotlib
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))

def plot_differences_catchments_years_by_obj_func_only_catchments(catchments, obj_func, amount_homogen):           
    """
    Plots the attributes of the catchments seperated by the most complex and most simple catchments
        """
    fig = plt.figure(figsize=(15,22.5))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[1,2], hspace=0.25)
    
    cat_grid = gridspec.GridSpecFromSubplotSpec(2,3, subplot_spec=outer[0], wspace=0.65, hspace=0.30)
    
    num_grid= gridspec.GridSpecFromSubplotSpec(3,3, subplot_spec=outer[1], wspace=0.2, hspace=0.30)
    axes = []

    # Get the predominant type for every year/catchment
    mean_obj_func = obj_func.mean(axis=0)
        
    # Find the year/catchment that have the highest and lowest objective function
    complex_catch_year = mean_obj_func[mean_obj_func < mean_obj_func.quantile(amount_homogen)].index.astype(float)
    simple_catch_year = mean_obj_func[mean_obj_func > mean_obj_func.quantile(1-amount_homogen)].index.astype(float)
    most_homogen = {"simple (n=18)": simple_catch_year, "complex (n=18)":complex_catch_year}
        
    # Create a figure for every attribute
    i = 0
    j = 0
    for att in catchments.columns:

        print(att)
        attributes_for_types = {}
        for type_catch in most_homogen.keys():
            homogen_type = most_homogen[type_catch]
            attributes_for_one_type = catchments.loc[homogen_type, att]
            attributes_for_one_type.name = type_catch
            attributes_for_one_type.reset_index(inplace=True, drop=True)
            attributes_for_types[type_catch] = attributes_for_one_type
     #       print(attributes_for_one_type)
            
        all_types = pd.concat([attributes_for_types[type_catch] for type_catch in attributes_for_types.keys()],axis=1)
        print()
        cmap = matplotlib.cm.get_cmap("PuBu")
        colors = [cmap(i / len(catchments[att].unique())) for i in range(len(catchments[att].unique())+1)]

        # if they are not flaot or int they should be categorical
        if catchments[att].dtypes != np.float64 and catchments[att].dtypes != np.int64:
            ax = plt.Subplot(fig, cat_grid[i]) 

            all_types_by_cat = pd.concat([all_types.groupby(col).count() for col in all_types.columns],axis=1, sort=True)
            all_types_by_cat = all_types_by_cat[all_types_by_cat.columns[::-1]]

            all_types_by_cat = all_types_by_cat.transpose()
            cat_for_whole_dataset = catchments[att].value_counts()
            cat_for_whole_dataset.name = "overall (n=89)"
            cat_for_whole_dataset = pd.DataFrame(cat_for_whole_dataset).transpose()
            all_types_by_cat = pd.concat([all_types_by_cat, cat_for_whole_dataset], sort=True)
            # Make it percent
            for row in all_types_by_cat.index:#
                all_types_by_cat.loc[row,:] = (all_types_by_cat.loc[row,:] / all_types_by_cat.loc[row,:].sum()) * 100
            # Give them the right order
            if att == 'Permeability [/]':
                all_types_by_cat= all_types_by_cat.transpose().reindex(["very low", "low/very low", "low",
                                     "moderate/low", "moderate", "mid/moderate",
                                     "mid", "variable"]).transpose()
            ax = all_types_by_cat.plot(kind="bar", stacked=True, ax=ax, color=colors, edgecolor="grey", zorder=5)
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[::-1], labels[::-1], loc=7, fontsize=7.5,bbox_to_anchor=(1.42, 0.5))
            for tick in ax.get_xticklabels():
                tick.set_rotation(360)
            ax.set_ylabel("Relative Frequency [%]", alpha=0.7)
            ax.set_xlabel(att, alpha=0.7)
            i += 1
            plt.setp(ax.get_xticklabels(), alpha=0.7, fontsize=7)


            

        else:
            ax = plt.Subplot(fig, num_grid[j]) 
            all_types = pd.concat([all_types, catchments[att]], axis=1)
            all_types.columns = ["simple (n=18)", "complex (n=18)", "overall (n=89)"]

            ax = sns.swarmplot(data=all_types, ax=ax, zorder=4, color="steelblue", size=3)
            ax = sns.boxplot(data=all_types, showcaps=False,boxprops={'facecolor':'None', "edgecolor":"grey", "zorder":5},
                             showfliers=False,whiskerprops={'linewidth':0,}, ax=ax, zorder=5, width=0.3)
            ax.set_ylabel(att, alpha=0.7)
            statistic, p_value = scipy.stats.f_oneway(all_types["simple (n=18)"].dropna(), 
                                                      all_types["complex (n=18)"].dropna(),
                                                      all_types["overall (n=89)"].dropna())
            bonferoni_p_val_correction = 20
            pval = p_value*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            pval = str(round(pval,3))
            if pval == "0.0":
                pval = "0"
            ax.set_title(" ANOVA P-Value: " + pval,alpha=0.7, fontsize=10)
            j += 1
            plt.setp(ax.get_xticklabels(), alpha=0.7, fontsize=8)


        ax.yaxis.grid(True, color="lightgrey",zorder=0)
        axes.append(ax)
        fig.add_subplot(ax)
        plt.setp(ax.get_yticklabels(), alpha=0.7)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
            
            
    # Add suptitles for gridspec
    rect_top = 0.5, 0.88, 0, 0.0  # lower, left, width, height (I use a lower height than 1.0, to place the title more visible)
    rect_bottom = 0.5, 0.59, 0, 0
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
    
    
    fig = plt.gcf()
    fig.set_size_inches(13,13)
    plt.savefig("all_together_most_extreme_catch.png", dpi=300,  bbox_inches="tight")
    plt.close()      

      
def format_p_val(pval):
    if pval > 0.01:
        return str(pval)
    elif pval < 0.0001:
        return "< 0.0001"
    elif pval < 0.001:
        return "< 0.001"
    else: 
        return "< 0.01"
    
    
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
   obj_func = pd.read_csv("obj_func_all_catchments.csv", sep=";", index_col=0)
   
   # Exclude non significant attributes

   catchments.drop(['Soil Depth [m]'],inplace=True, axis=1)
   plot_differences_catchments_years_by_obj_func_only_catchments(catchments, obj_func, 0.2)
