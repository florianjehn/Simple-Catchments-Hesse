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

def plot_differences_catchments_years_by_least_squares_only_catchments(catchments, least_squares, amount_homogen):           
    """
    Plots the attributes of the catchments seperated by the most complex and most simple catchments
        """
    fig = plt.figure(figsize=(15,22.5))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[1,1], hspace=0.15)
    
    cat_grid = gridspec.GridSpecFromSubplotSpec(2,3, subplot_spec=outer[0], wspace=0.5, hspace=0.15)
    
    num_grid= gridspec.GridSpecFromSubplotSpec(2,3, subplot_spec=outer[1], wspace=0.2, hspace=0.15)
    axes = []

    # Get the predominant type for every year/catchment
    mean_least_squares = least_squares.mean(axis=0)
        
    # Find the year/catchment that have the highest and lowest least square error
    simple_catch_year = mean_least_squares[mean_least_squares < mean_least_squares.quantile(amount_homogen)].index.astype(float)
    complex_catch_year = mean_least_squares[mean_least_squares > mean_least_squares.quantile(1-amount_homogen)].index.astype(float)
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
     #   print(all_types)

        # if they are not flaot or int they should be categorical
        if catchments[att].dtypes != np.float64 and catchments[att].dtypes != np.int64:
            ax = plt.Subplot(fig, cat_grid[i]) 

            all_types_by_cat = pd.concat([all_types.groupby(col).count() for col in all_types.columns],axis=1, sort=True)
            all_types_by_cat = all_types_by_cat[all_types_by_cat.columns[::-1]]
            cmap = matplotlib.cm.get_cmap("PuBu")
            colors = [cmap(i / len(all_types_by_cat.transpose().columns)) for i in range(len(all_types_by_cat.transpose().columns)+1)]

            all_types_by_cat = all_types_by_cat.transpose()
            cat_for_whole_dataset = catchments[att].value_counts()
            cat_for_whole_dataset.name = "overall (n=90)"
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
            elif att == "
            ax = all_types_by_cat.plot(kind="bar", stacked=True, ax=ax, color=colors, edgecolor="grey", zorder=5)
            legend = ax.legend(loc=7, fontsize=7,bbox_to_anchor=(1.3, 0.5))
            for tick in ax.get_xticklabels():
                tick.set_rotation(360)
            ax.set_ylabel("Relative Frequency [%]", alpha=0.7)
            ax.set_xlabel(att, alpha=0.7)
            i += 1

            

        else:
            ax = plt.Subplot(fig, num_grid[j]) 
            all_types = pd.concat([all_types, catchments[att]], axis=1)
            all_types.columns = ["simple (n=18)", "complex (n=18)", "overall (n=90)"]

            ax = sns.swarmplot(data=all_types, ax=ax, zorder=4, color="steelblue", size=4)
            ax = sns.boxplot(data=all_types, showcaps=False,boxprops={'facecolor':'None', "edgecolor":"grey", "zorder":5},
                             showfliers=False,whiskerprops={'linewidth':0,}, ax=ax, zorder=5, width=0.3)
            ax.set_ylabel(att, alpha=0.7)
            statistic, p_value = scipy.stats.f_oneway(all_types["simple (n=18)"].dropna(), 
                                                      all_types["complex (n=18)"].dropna(),
                                                      all_types["overall (n=90)"].dropna())
            bonferoni_p_val_correction = 21
            pval = p_value*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            ax.set_title(" ANOVA P-Value: " + str(round(pval,3)),alpha=0.7)
            j += 1

        ax.yaxis.grid(True, color="lightgrey",zorder=0)
        axes.append(ax)
        fig.add_subplot(ax)
        plt.setp(ax.get_yticklabels(), alpha=0.7)
        plt.setp(ax.get_xticklabels(), alpha=0.7, fontsize=8)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
            
    fig = plt.gcf()
    plt.savefig("all_together_most_extreme_catch.png", dpi=150,  bbox_inches="tight")
    plt.close()      

def plot_differences_catchments_years_by_least_squares_all_together(catchments, years, least_squares, amount_homogen):           
    """
    Plots the attributes of the years or catchments in a scatterplot 
    with the least squares for those catchments. Axis = 0 --> columns/catchments
    axis = 1 --> rows/years
        """
    fig = plt.figure(figsize=(20,30))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[5,2], hspace=0.15)
    
    catchments_grid = gridspec.GridSpecFromSubplotSpec(4,3, subplot_spec=outer[0], wspace=0.2, hspace=0.15)
    
    years_grid = gridspec.GridSpecFromSubplotSpec(2,3, subplot_spec=outer[1], wspace=0.2, hspace=0.15)
    axes = []

    for axis, catch_year in enumerate([catchments, years]):
        print(axis)

        # Get the predominant type for every year/catchment
        if axis == 0:
            mean_least_squares = least_squares.mean(axis=0)
        else:
            mean_least_squares = least_squares.mean(axis=1)
            
        # Find the year/catchment that have the highest and lowest least square error
        simple_catch_year = mean_least_squares[mean_least_squares < mean_least_squares.quantile(amount_homogen)].index.astype(float)
        complex_catch_year = mean_least_squares[mean_least_squares > mean_least_squares.quantile(1-amount_homogen)].index.astype(float)
        most_homogen = {"simple": simple_catch_year, "complex":complex_catch_year}
            
        # Create a figure for every attribute
        for i, att in enumerate(catch_year.columns):
            ax = plt.Subplot(fig, catchments_grid[i]) if axis == 0 else plt.Subplot(fig, years_grid[i])

            print(att)
            attributes_for_types = {}
            for type_catch in most_homogen.keys():
                homogen_type = most_homogen[type_catch]
                attributes_for_one_type = catch_year.loc[homogen_type, att]
                attributes_for_one_type.name = type_catch
                attributes_for_one_type.reset_index(inplace=True, drop=True)
                attributes_for_types[type_catch] = attributes_for_one_type
         #       print(attributes_for_one_type)
                
            all_types = pd.concat([attributes_for_types[type_catch] for type_catch in attributes_for_types.keys()],axis=1)
         #   print(all_types)
    
            # if they are not flaot or int they should be categorical
            if catch_year[att].dtypes != np.float64 and catch_year[att].dtypes != np.int64:
                all_types_by_cat = pd.concat([all_types.groupby(col).count() for col in all_types.columns],axis=1, sort=True)
                all_types_by_cat = all_types_by_cat[all_types_by_cat.columns[::-1]]
                cmap = matplotlib.cm.get_cmap("PuBu")
                colors = [cmap(i / len(all_types_by_cat.transpose().columns)) for i in range(len(all_types_by_cat.transpose().columns))]
                ax = all_types_by_cat.transpose().plot(kind="bar", stacked=True, ax=ax, color=colors, edgecolor="grey", zorder=5)
                legend = ax.legend(loc=10, fontsize=7)
                for tick in ax.get_xticklabels():
                    tick.set_rotation(360)
                ax.set_ylabel("Frequency", alpha=0.7)
                ax.set_xlabel(att, alpha=0.7)

                
    
            else:
            
                ax = sns.swarmplot(data=all_types, ax=ax, zorder=5, color="steelblue")
                ax = sns.boxplot(data=all_types, showcaps=False,boxprops={'facecolor':'None', "edgecolor":"lightgrey"},
                                 showfliers=False,whiskerprops={'linewidth':0,}, ax=ax, zorder=4, width=0.3)
                ax.set_ylabel(att, alpha=0.7)

            ax.yaxis.grid(True, color="lightgrey",zorder=0)
            axes.append(ax)
            fig.add_subplot(ax)
            plt.setp(ax.get_yticklabels(), alpha=0.7)
            plt.setp(ax.get_xticklabels(), alpha=0.7)
            ax.tick_params(axis=u'both', which=u'both',length=0)
            for spine in ax.spines.values():
                spine.set_visible(False)
            
    fig = plt.gcf()
    plt.savefig("all_together_most_extreme.png", dpi=150,  bbox_inches="tight")
    plt.close()      


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
        attributes_for_types = {}
        for type_catch in most_homogen.keys():
            homogen_type = most_homogen[type_catch]
            attributes_for_one_type = attributes.loc[homogen_type, att]
            attributes_for_one_type.name = type_catch
            attributes_for_one_type.reset_index(inplace=True, drop=True)
            attributes_for_types[type_catch] = attributes_for_one_type
     #       print(attributes_for_one_type)
            
        all_types = pd.concat([attributes_for_types[type_catch] for type_catch in attributes_for_types.keys()],axis=1)

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
            statistic, p_value = scipy.stats.ranksums(all_types["simple"], all_types["complex"])
            ax.set_title(year_catch + "; attribute: " + att + "; p_val: "+str(np.round(p_value,decimals=3)) + "; n="+str(len(simple_catch_year)))
            
            
        fig = plt.gcf()
        fig.tight_layout()
        plt.savefig(year_catch + "_attribute_" + att[:-4]+ ".png", dpi=150,  bbox_inches="tight")
        plt.close()      
        
        
if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments()
   years = ccdt.get_attributes_years()
   least_squares = pd.read_csv("least_square_all_catchments.csv", sep=";", index_col=0)
#   plot_differences_catchments_years_by_least_squares(least_squares, catchments , 0.2, "catch")
#   plot_differences_catchments_years_by_least_squares(least_squares, years, 0.2, "year")
   
   # Exclude non significant attributes
   years.drop(['soil_temp_C_1991_2018', 'mean_air_temperature',
               'Precipitation [mm]', 'Snow Fraction [%]',
               'Aridity [/]'],inplace=True, axis=1)
   catchments.drop(['Land Use [/]', 'Area [km²]', 'Soil Depth [m]',
                    'Slope [/]'],inplace=True, axis=1)
#   plot_differences_catchments_years_by_least_squares_all_together(catchments, years, least_squares, 0.2)
   plot_differences_catchments_years_by_least_squares_only_catchments(catchments, least_squares, 0.2)
