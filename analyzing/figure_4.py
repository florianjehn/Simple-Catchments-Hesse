# -*- coding: utf-8 -*-
"""
Created on Fri Aug 02 13:13:19 2019

@author: Florian Ulrich Jehn
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))


def plot_Q_vs_cumdS_scatter(dataframes, water_year=True):
    """
    Plots Q vs cumdS for seperated by year and river
    """
    import matplotlib
    # Agg stops matplotlib from opening a new window every time
    matplotlib.use('Agg')
    for catch in dataframes.keys():
        df = dataframes[catch]
        if water_year:
            grouped_years = df.groupby("water_year")
        else:
            grouped_years = df.groupby(df.index.year)
        for year, year_df in grouped_years:
            # Skip half empty water years
            if water_year and (year == 1991 or year == 2019):
                continue
            if water_year:
                c = list(year_df.loc[year_df["P"]==0,:].month_of_water_year)
            else:
                c = list(year_df.loc[year_df["P"]==0,:].index.month)
            year_df["cdS"] = np.cumsum(year_df["dS"])
            cdS = year_df.loc[year_df["P"] == 0, "cdS"]
            Q = year_df.loc[year_df["P"] == 0,"Q"]
            sc = plt.scatter(cdS, Q, c=c, cmap="coolwarm", edgecolors ="black", linewidths =0.2, zorder=5)
            plt.title("Catchment: " + str(catch) + ", Year: " + str(year), alpha=0.7)
            plt.xlabel("Cummulative Storage Change [mm]", alpha=0.7)
            plt.ylabel("Discharge [mm $d^{-1}$]", alpha=0.7)
            try:
                legend = plt.legend(*sc.legend_elements(), title="Hydrological Month")
                for text in legend.get_texts():
                    text.set_color("#797979")  
                legend.get_title().set_color("#797979")
            except ValueError as val:
                print(catch)
                print(year)
                print(val)
            # Make the plot nicer    
            ax = plt.gca()
            ax.tick_params(axis=u'both', which=u'both',length=0)
            ax.grid(True, color="lightgrey", zorder=0)
            for spine in ax.spines.values():
                spine.set_visible(False)    
            plt.setp(ax.get_xticklabels(), alpha=0.7)
            plt.setp(ax.get_yticklabels(), alpha=0.7)
            fig = plt.gcf()
            fig.set_size_inches(8,8)
            plt.savefig("q_vs_dS/"+ str(catch) + "_" + str(year) + "_no_rain.png", dpi=150, bbox_inches="tight")
            plt.close()


def calculate_dS(dataframes:dict):
    """
    Calculates the storage change for every day and adds it to the dataframes
    """
    for catch in dataframes.keys():
        df = dataframes[catch]
        df["dS"] = df.P - df.E_cor - df.Q
        

if __name__ == '__main__':
    # This creates all the Q vs. dS plots. Figure 3 is made from a selection
    # of them by hand. 
    import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
    in_dfs = ccdt.get_table_dict(calc_water_year=True)
    dataframes = {}
    for catch in list(in_dfs.keys())[:]:
        # Skip catchments with much missing or stepwise data
        if catch in [23950104, 24781159, 24781206, 428832990, 42870057]:
            print("Skipped: " + str(catch))
            continue
        dataframes[catch] = in_dfs[catch]

    
 #   plot_Q_vs_cumdS_scatter(dataframes, water_year=True)

       

