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


def heatmap(obj_func):
    """Creats a heatmap of the obj_func with bar plots on each
    side to mark the mean """
    # Create the gridspec
    gs = gridspec.GridSpec(2,2, 
                           height_ratios=[1,3],
                           width_ratios = [30, 1], 
                           hspace=0.00, 
                           wspace=-1.513)
    fig = plt.gcf()
    # Plot the heatmap
    ax_heatmap = fig.add_subplot(gs[1,0])
    obj_func = obj_func.copy()
    obj_func = obj_func.reindex(obj_func.mean().sort_values().index,axis=1)
    obj_func = obj_func.transpose()
    # Reset index to make indentification easier
    obj_func = obj_func.reset_index()
    obj_func.index = obj_func.index + 1
    del(obj_func["index"])

    sns.heatmap(obj_func, square=True, cmap="Blues",  yticklabels=True,
                     cbar_kws = dict(use_gridspec=False,location="left",shrink= 0.3, pad=0.01), 
                     ax=ax_heatmap, linecolor="grey", linewidths=0.1)
    ax_heatmap.set_ylabel("Catchments", alpha=0.7)
    ax_heatmap.set_xlabel("Years", alpha=0.7)
    ax_heatmap.tick_params(axis=u'both', which=u'both',length=0)
    plt.setp(ax_heatmap.get_xticklabels(), alpha=0.7)
    plt.setp(ax_heatmap.get_yticklabels(), alpha=0.7)
    
    # Set the visibility of the ticklabeobj_func
    temp = ax_heatmap.xaxis.get_ticklabels()
    temp = list(set(temp) - set(temp[1::2]))
    for label in temp:
        label.set_visible(False)
        
    temp = ax_heatmap.yaxis.get_ticklabels()
    temp = list(set(temp) - set(temp[1::2]))
    for label in temp:
        label.set_visible(False)


    cbar = ax_heatmap.collections[0].colorbar
    # here set the labeobj_funcize by 20
    cbar.ax.set_ylabel("KGE [/]", alpha=0.7)
    plt.setp(cbar.ax.get_yticklabels(), alpha=0.7)
    cbar.ax.tick_params(color="lightgrey")
    # Calculate the averages for the bar plots
    catchment_avg = obj_func.mean(axis=1).sort_values(ascending =False)
    year_avg = pd.DataFrame(obj_func.mean())

    # Plot the barplots
    # Dummy plot
    ax_bar_top = fig.add_subplot(gs[0,0])
    year_avg.plot.bar(ax=ax_bar_top, facecolor="steelblue",edgecolor="black", linewidth=0.1, zorder=5)
    ax_bar_top.set_ylim(0,0.8)
    ax_bar_top.get_legend().remove()
    ax_bar_right = fig.add_subplot(gs[1,1])
    catchment_avg.plot.barh(ax=ax_bar_right, facecolor="steelblue",edgecolor="black",linewidth =0.1, zorder=5)
    ax_bar_right.xaxis.set_ticks(np.arange(0, 0.81, 0.2))

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
    ax_bar_top.set_title("Yearly Mean of the KGE [/]", alpha=0.7, fontsize=fontsize)      
    ax_bar_right.set_ylabel("Catchment Mean of the KGE [/]\n", alpha=0.7, labelpad=-120, rotation=270, fontsize=fontsize)

    for tick in ax_bar_right.get_xticklabels():
        tick.set_rotation(90)     
    # Adjust top plot finely grained
    
    ax_bar_top.set_position([0.621,0.69, 0.175, 0.1])
    # Finishing touches    
    fig = plt.gcf()
    fig.set_size_inches(15,15)
    plt.savefig("heatmap.png", dpi=500, bbox_inches="tight")
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
                        # Soiobj_func
                        'Soil Depth [m]','Soil Texture [/]','Soil Type [/]', 
                        # Groundwater
                        'Aquifer Conductivity [/]', 'Geology Type [/]', 'Ground Water Recharge [mm]',        'Permeability [/]'

        ], axis=1)
   years = ccdt.get_attributes_years()
   obj_func = pd.read_csv("obj_func_all_catchments.csv", sep=";", index_col=0)
   del(obj_func["41510205"])
   heatmap(obj_func)
