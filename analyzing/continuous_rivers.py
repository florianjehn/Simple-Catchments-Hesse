import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import seaborn as sns
import scipy
from matplotlib import gridspec
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))


            
    
def scatter_swarm_lse_all_only_catchments(catchments, least_squares):           
    """
    Plots the scatter and violin plots only for the catchments
    
    """
    fig = plt.figure(figsize=(12.5 ,15))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2,3], hspace=0.4)
    
    cat_grid = gridspec.GridSpecFromSubplotSpec(2,3, subplot_spec=outer[0], wspace=0.3, hspace=1)
    
    num_grid = gridspec.GridSpecFromSubplotSpec(3,3, subplot_spec=outer[1], wspace=0.3, hspace=0.5)
    
    axes = []
    j = 0
    i = 0
    for attribute in catchments.columns:
        
        print(attribute)
        if attribute == "gauge":
            continue
        iterate = least_squares.columns
        collect = []
        for single_catch in iterate:
            # Skip catchments with much missing or stepwise data
            if single_catch in ["23950104", "24781159", "24781206", "428832990", "42870057"]:
                print("Skipped: " + str(single_catch))
                continue
            least_square_single = least_squares.loc[:,single_catch]
            least_square_single.name = "catchment_least_square"
            current_catch_att = catchments.loc[ int(single_catch), attribute]
            # Make attribute as long as the least squares
            current_catch_att = pd.Series([current_catch_att] * len(least_square_single), index=least_square_single.index)
            current_catch_att.name=attribute
            combined = pd.concat([least_square_single, pd.Series(current_catch_att)],axis=1)
            collect.append(combined)
        all_data_attribute = pd.concat(collect,ignore_index=True)

        fig = plt.gcf()
        bonferoni_p_val_correction = 21
        if all_data_attribute[attribute].dtype != float:
            ax = plt.Subplot(fig, cat_grid[i])
            sns.swarmplot(y="catchment_least_square", data=all_data_attribute, x=attribute,ax=ax, color="steelblue", zorder=5, size=0.8)
            sns.boxplot(y="catchment_least_square", data=all_data_attribute, x=attribute, showcaps=False,boxprops={'facecolor':'None', "edgecolor":"grey", "zorder":5,'linewidth':2},
                                                showfliers=False,whiskerprops={'linewidth':0,}, ax=ax, zorder=5, width=0.4)
            values_per_group = [col.dropna() for col_name, col in all_data_attribute.groupby(attribute)["catchment_least_square"]]

            statistic, pval = scipy.stats.f_oneway(*values_per_group)
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)
            pval = pval*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            ax.set_title("ANOVA P-Value: " + str(round(pval,3)),alpha=0.7)
            ax.set_xlabel(attribute, alpha=0.7)
            ax.yaxis.grid(True, color="lightgrey")
            if attribute == "Land Use [/]":
                ax.set_xlim(-0.5,2.5)
            i += 1
                

        else:
            
            ax = plt.Subplot(fig, num_grid[j])
            x = all_data_attribute[attribute].astype(float)
            y = all_data_attribute["catchment_least_square"]
            xy = pd.concat([x,y],axis=1)
            xy.dropna(inplace=True)
            results = scipy.stats.linregress(xy)           
            ax = sns.regplot(x,y, marker="o",
                        scatter_kws={"s":0.2, "facecolor":"steelblue", "edgecolor":"steelblue", "zorder":4, "alpha":0.5},
                        line_kws={"color":"black", "linewidth":"0.75", "zorder":5}, ax=ax)
            ax.set_xlabel(attribute,   alpha=0.7)
            ax.grid(True, color="lightgrey",zorder=0)
            ax.set_xlim(all_data_attribute[attribute].min(), all_data_attribute[attribute].max())
            pval = results[3]*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            ax.set_title("Regression Trend P-Value: " + str(round(pval,3)),alpha=0.7)
            j += 1
        ax.set_ylabel("Mean Least Squares [/]",alpha=.7) 
        # Make nicer
        plt.setp(ax.get_yticklabels(), alpha=0.7)
        plt.setp(ax.get_xticklabels(), alpha=0.7)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        
        axes.append(ax)
        fig.add_subplot(ax)
        
        
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

    plt.savefig("catchment_regressions_attributes.png", dpi=300, bbox_inches="tight")
    plt.close()
            
        
        
def find_unique_pairs(cats):
    """ 
    Finds all unique combinatino of the categories in cats and returns a list
    of pairs in tuples
    """
    unique_pairs = []    
    for a in cats:
        for b in cats:
            if a != b:
                unique_pairs.append(tuple(sorted((a,b))))
    return list(set(unique_pairs))


def heatmap_ls(least_squares):
    """Creats a heatmap of the least squares with bar plots on each
    side to mark the mean """
    # Create the gridspec
    gs = gridspec.GridSpec(2,2, height_ratios=[1,3], width_ratios = [30, 1], hspace=0, wspace=-1.513)
    fig = plt.gcf()
    # Plot the heatmap
    ax_heatmap = fig.add_subplot(gs[1,0])
    ls = least_squares.copy()
    ls = ls.reindex(ls.mean().sort_values().index,axis=1)
    ls = ls.transpose()
    # Reset index to make indentification easier
    ls = ls.reset_index()
    ls.index = ls.index + 1
    del(ls["index"])

    sns.heatmap(ls, square=True, cmap="Blues",  yticklabels=True,
                     cbar_kws = dict(use_gridspec=False,location="left",shrink= 0.3, pad=0.01), 
                     ax=ax_heatmap, linecolor="grey", linewidths=0.1)
    ax_heatmap.set_ylabel("Catchments", alpha=0.7)
    ax_heatmap.set_xlabel("Years", alpha=0.7)
    ax_heatmap.tick_params(axis=u'both', which=u'both',length=0)
    plt.setp(ax_heatmap.get_xticklabels(), alpha=0.7)
    plt.setp(ax_heatmap.get_yticklabels(), alpha=0.7)
    
    # Set the visibility of the ticklabels
    temp = ax_heatmap.xaxis.get_ticklabels()
    temp = list(set(temp) - set(temp[1::2]))
    for label in temp:
        label.set_visible(False)
        
    temp = ax_heatmap.yaxis.get_ticklabels()
    temp = list(set(temp) - set(temp[1::2]))
    for label in temp:
        label.set_visible(False)


    cbar = ax_heatmap.collections[0].colorbar
    # here set the labelsize by 20
    cbar.ax.set_ylabel("Mean Least Squares [/]", alpha=0.7)
    plt.setp(cbar.ax.get_yticklabels(), alpha=0.7)
    cbar.ax.tick_params(color="lightgrey")
    # Calculate the averages for the bar plots
    catchment_avg = ls.mean(axis=1).sort_values(ascending =False)
    year_avg = pd.DataFrame(ls.mean())

    # Plot the barplots
    # Dummy plot
    ax_bar_top = fig.add_subplot(gs[0,0])
    year_avg.plot.bar(ax=ax_bar_top, facecolor="steelblue",edgecolor="black", linewidth=0.1, zorder=5)
    ax_bar_top.get_legend().remove()
    ax_bar_right = fig.add_subplot(gs[1,1])
    catchment_avg.plot.barh(ax=ax_bar_right, facecolor="steelblue",edgecolor="black",linewidth =0.1, zorder=5)
    # Remove all borders and stuff
    for ax in [ax_bar_top, ax_bar_right]:
        for spine in ax.spines.values():
            spine.set_visible(False)
            plt.setp(ax.get_yticklabels(), alpha=0)
            plt.setp(ax.get_xticklabels(), alpha=0)
            ax.tick_params(axis=u'both', which=u'both',length=0)
   
    ax_bar_top.yaxis.grid(True, color="lightgrey",zorder=0)
    ax_bar_right.xaxis.grid(True, color="lightgrey",zorder=0)
    plt.setp(ax_bar_top.get_yticklabels(), alpha=0.7)
    plt.setp(ax_bar_top.get_xticklabels(), alpha=0)
    plt.setp(ax_bar_right.get_yticklabels(), alpha=0)
    plt.setp(ax_bar_right.get_xticklabels(), alpha=0.7) 
    fontsize=10
    ax_bar_top.set_title("Yearly Mean of the Mean Least Squares [/]", alpha=0.7, fontsize=fontsize)      
    ax_bar_right.set_ylabel("Catchment Mean of the Mean Least Squares [/]", alpha=0.7, labelpad=-120, rotation=270, fontsize=fontsize)

    for tick in ax_bar_right.get_xticklabels():
        tick.set_rotation(90)     
    # Adjust top plot finely grained
    
    ax_bar_top.set_position([0.618,0.69, 0.175, 0.1])
    # Finishing touches    
    fig = plt.gcf()
    fig.set_size_inches(15,15)
    plt.savefig("heatmap_lse.png", dpi=500, bbox_inches="tight")
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
   years = ccdt.get_attributes_years()
   least_squares = pd.read_csv("least_square_all_catchments.csv", sep=";", index_col=0)
   del(least_squares["41510205"])
   heatmap_ls(least_squares)
   scatter_swarm_lse_all_only_catchments(catchments, least_squares)
