import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import seaborn as sns
import scipy
import statannot
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))



def scatter_violin_least_squares_attribute(catch_year, least_squares, axis):
    """
    Plots the attributes of the years or catchments in a scatterplot 
    with the least squares for those catchments. Axis = 0 --> columns/catchments
    axis = 1 --> rows/years
        """
    for attribute in catch_year.columns:
        if attribute == "gauge":
            continue
        iterate = least_squares.index if axis == 1 else least_squares.columns
        collect = []
        for single_catch_year in iterate:
            # Skip catchments with much missing or stepwise data
            if single_catch_year in ["23950104", "24781159", "24781206", "428832990", "42870057"]:
                print("Skipped: " + str(single_catch_year))
                continue
            if axis == 1:
                least_square_single = least_squares.loc[single_catch_year,:] 
            elif axis == 0:
                least_square_single = least_squares.loc[:,single_catch_year]
            least_square_single.name = "catchment_least_square"
            current_catch_att = catch_year.loc[ int(single_catch_year), attribute]
            # Make attribute as long as the least squares
            current_catch_att = pd.Series([current_catch_att] * len(least_square_single), index=least_square_single.index)
            current_catch_att.name=attribute
            combined = pd.concat([least_square_single, pd.Series(current_catch_att)],axis=1)
            collect.append(combined)
        all_data_attribute = pd.concat(collect,ignore_index=True)
        
        ax = plt.gca()
        fig = plt.gcf()
        looking_at = "year" if axis == 1 else "catchment"
        if all_data_attribute[attribute].dtype != float:
            sns.violinplot(y="catchment_least_square", data=all_data_attribute, x=attribute,ax=ax)
#            pairs = find_unique_pairs(all_data_attribute[attribute])
#            statannot.add_stat_annotation(ax, data=all_data_attribute, x=attribute,y="catchment_least_square",
#                                          box_pairs=pairs)
            ax.set_title(looking_at + ": " + attribute)

        else:
            x = all_data_attribute[attribute].astype(float)
            y = all_data_attribute["catchment_least_square"]
            xy = pd.concat([x,y],axis=1)
            xy.dropna(inplace=True)
            results = scipy.stats.linregress(xy)           
            ax = sns.regplot(x,y, marker="o",
                        scatter_kws={"s":0.2, "facecolor":"blue", "edgecolor":None},
                        line_kws={"color":"black", "linewidth":"0.75"})
            bonferoni_p_val_correction = 23
            ax.set_title(looking_at + ": " + attribute + " pval: " +str(round(results[3]*bonferoni_p_val_correction,5)))
            
        
        ax.set_xlabel(attribute)
        ax.set_ylabel("least square error")
        fig.tight_layout()
        plt.savefig(attribute + ".png", dpi=200)
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
    ls = least_squares.copy().transpose()
    print(ls)
    ls["catch_avg"] = ls.mean(axis=1)
    year_avg = pd.DataFrame(ls.mean()).transpose()
    year_avg.index = ["year_avg"]
    ls = pd.concat([year_avg, ls])
    ls.loc[ "year_avg", "catch_avg"] = None
    ax = sns.heatmap(ls, square=True, cmap="PuBu", yticklabels=False, xticklabels=1)
    ax.hlines(1, *ax.get_xlim(), color="black", linewidth=1)
    ax.vlines(ls.shape[1]-1, *ax.get_ylim(), color="black", linewidth=1)
    fig = plt.gcf()
    fig.set_size_inches(20,20)
    plt.savefig("heatmap_lse.png", dpi=200, bbox_inches="tight")
    plt.close()
    
    
def regplot_kge_lse(lse, kge):
    """
    Creates a regplot for all values of the least squares and the KGE for 
    all catchments and all years. 
    """
    new = pd.DataFrame(columns = ["kge", "lse"], index=list(range(2430)))
    new["kge"] = pd.concat([kge[col] for col in kge]).reset_index(drop=True)
    new["lse"] = pd.concat([lse[col] for col in lse]).reset_index(drop=True)
    ax = sns.regplot(y="kge", x="lse", data=new,marker="o",
                        scatter_kws={"s":0.5, "facecolor":"blue", "edgecolor":None},
                        line_kws={"color":"black", "linewidth":"0.75"})
    results = scipy.stats.linregress(new.dropna())
    ax.set_title("pval: " +str(round(results[3]*23,5)))
    plt.savefig("kge_lse.png", dpi=200)
    plt.close()


if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments_num()
   years = ccdt.get_attributes_years()
   least_squares = pd.read_csv("least_square_all_catchments.csv", sep=";", index_col=0)
   del(least_squares["41510205"])
   heatmap_ls(least_squares)
#   scatter_violin_least_squares_attribute(catchments, least_squares, 0)
#   scatter_violin_least_squares_attribute(years, least_squares, 1)
#   kge = pd.read_csv("kge_all_years_catch.csv", sep=";", index_col=0)
#   regplot_kge_lse(least_squares, kge)