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


            
    
def scatter_swarm_all_only_catchments(catchments, obj_func):           
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
        iterate = obj_func.columns
        collect = []
        for single_catch in iterate:
            # Skip catchments with much missing or stepwise data
            if single_catch in ["23950104", "24781159", "24781206", "428832990", "42870057"]:
                print("Skipped: " + str(single_catch))
                continue
            obj_func_single = obj_func.loc[:,single_catch]
            obj_func_single.name = "catchment_obj_func"
            current_catch_att = catchments.loc[ int(single_catch), attribute]
            # Make attribute as long as the least squares
            current_catch_att = pd.Series([current_catch_att] * len(obj_func_single), index=obj_func_single.index)
            current_catch_att.name=attribute
            combined = pd.concat([obj_func_single, pd.Series(current_catch_att)],axis=1)
            collect.append(combined)
        all_data_attribute = pd.concat(collect,ignore_index=True)

        fig = plt.gcf()
        bonferoni_p_val_correction = 24
        if all_data_attribute[attribute].dtype != float:
            ax = plt.Subplot(fig, cat_grid[i])
            sns.swarmplot(y="catchment_obj_func", data=all_data_attribute, x=attribute,ax=ax, color="steelblue", zorder=5, size=0.8)
            sns.boxplot(y="catchment_obj_func", data=all_data_attribute, x=attribute, showcaps=False,boxprops={'facecolor':'None', "edgecolor":"grey", "zorder":5,'linewidth':2},
                                                showfliers=False,whiskerprops={'linewidth':0,}, ax=ax, zorder=5, width=0.4)
            values_per_group = [col.dropna() for col_name, col in all_data_attribute.groupby(attribute)["catchment_obj_func"]]

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
            y = all_data_attribute["catchment_obj_func"]
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
        ax.set_ylabel("KGE [/]",alpha=.7) 
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
   obj_func = pd.read_csv("obj_func_all_catchments.csv", sep=";", index_col=0)
   del(obj_func["41510205"])
   scatter_swarm_all_only_catchments(catchments, obj_func)
