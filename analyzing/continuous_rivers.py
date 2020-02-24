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


def scatter_violin_lse_all_together(catchments, years, least_squares):           
    """
    Plots the attributes of the years and catchments in one big figure.
        """
    fig = plt.figure(figsize=(20,30))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[16,9], hspace=0.15)
    
    catchments_grid = gridspec.GridSpecFromSubplotSpec(4,4, subplot_spec=outer[0], wspace=0.2, hspace=0.6)
    
    years_grid = gridspec.GridSpecFromSubplotSpec(2,4, subplot_spec=outer[1], wspace=0.2, hspace=0.2)
    
    axes = []
    years.drop(["mean_air_temperature", "soil_temp_C_1991_2018"], inplace=True, axis=1)
    # Revert catchment columns
    for axis, catch_year in enumerate([catchments, years]):
        print(axis)
        for i,attribute in enumerate(catch_year.columns):
            print(attribute)
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
            ax = plt.Subplot(fig, catchments_grid[i]) if axis == 0 else plt.Subplot(fig, years_grid[i])

            fig = plt.gcf()
            bonferoni_p_val_correction = 24
            if all_data_attribute[attribute].dtype != float:
                sns.violinplot(y="catchment_least_square", data=all_data_attribute, x=attribute,ax=ax, color="lightsteelblue", zorder=5)
             #   print(all_data_attribute)
                values_per_group = [col.dropna() for col_name, col in all_data_attribute.groupby(attribute)["catchment_least_square"]]
    #            for key, val in values_per_group.items():
    #                print(key)
    #                print(val)
                statistic, pval = scipy.stats.f_oneway(*values_per_group)
                for tick in ax.get_xticklabels():
                    tick.set_rotation(50)
                pval = pval*bonferoni_p_val_correction
                pval = 1 if pval > 1 else pval
                ax.set_title("P-Value: " + str(round(pval,3)),alpha=0.7)
                ax.set_xlabel(attribute, alpha=0.7)
                if attribute == "Land Use [/]":
                    ax.set_xlim(-0.5,2.5)
                    
    
            else:
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
                ax.set_title("P-Value: " + str(round(pval,3)),alpha=0.7)

            ax.set_ylabel("Mean Least Square Error [/]",alpha=.7) 
            # Make nicer
            plt.setp(ax.get_yticklabels(), alpha=0.7)
            plt.setp(ax.get_xticklabels(), alpha=0.7)
            ax.tick_params(axis=u'both', which=u'both',length=0)
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            
            axes.append(ax)
            fig.add_subplot(ax)

    plt.savefig("all_regressions_attributes.png", dpi=200, bbox_inches="tight")
    plt.close()
            
    
def scatter_violin_lse_all_only_catchments(catchments, least_squares):           
    """
    Plots the scatter and violin plots only for the catchments
    
    """
    fig = plt.figure(figsize=(15 ,22.5))
    outer = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2,3], hspace=0.2)
    
    cat_grid = gridspec.GridSpecFromSubplotSpec(2,3, subplot_spec=outer[0], wspace=0.3, hspace=0.6)
    
    num_grid = gridspec.GridSpecFromSubplotSpec(3,3, subplot_spec=outer[1], wspace=0.3, hspace=0.3)
    
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
            sns.violinplot(y="catchment_least_square", data=all_data_attribute, x=attribute,ax=ax, color="lightsteelblue", zorder=5)
         #   print(all_data_attribute)
            values_per_group = [col.dropna() for col_name, col in all_data_attribute.groupby(attribute)["catchment_least_square"]]
#            for key, val in values_per_group.items():
#                print(key)
#                print(val)
            statistic, pval = scipy.stats.f_oneway(*values_per_group)
            for tick in ax.get_xticklabels():
                tick.set_rotation(50)
            pval = pval*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            ax.set_title("P-Value: " + str(round(pval,3)),alpha=0.7)
            ax.set_xlabel(attribute, alpha=0.7)
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
            ax.set_title("P-Value: " + str(round(pval,3)),alpha=0.7)
            j += 1
        ax.set_ylabel("Mean Least Square Error [/]",alpha=.7) 
        # Make nicer
        plt.setp(ax.get_yticklabels(), alpha=0.7)
        plt.setp(ax.get_xticklabels(), alpha=0.7)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        
        axes.append(ax)
        fig.add_subplot(ax)

    plt.savefig("catchment_regressions_attributes.png", dpi=200, bbox_inches="tight")
    plt.close()
            


def scatter_violin_least_squares_attribute(catch_year, least_squares, axis):
    """
    Plots the attributes of the years or catchments in a scatterplot 
    with the least squares for those catchments. Axis = 0 --> columns/catchments
    axis = 1 --> rows/years
        """
    for attribute in catch_year.columns:
        print(attribute)
        if attribute == "gauge":
            continue
        if "temp" in attribute:
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
        looking_at = "Year Attribute" if axis == 1 else "Catchment Attribute"
        bonferoni_p_val_correction = 24

        if all_data_attribute[attribute].dtype != float:
            sns.violinplot(y="catchment_least_square", data=all_data_attribute, x=attribute,ax=ax, color="lightsteelblue", zorder=5)
         #   print(all_data_attribute)
            values_per_group = [col.dropna() for col_name, col in all_data_attribute.groupby(attribute)["catchment_least_square"]]
#            for key, val in values_per_group.items():
#                print(key)
#                print(val)
            statistic, pval = scipy.stats.f_oneway(*values_per_group)
            for tick in ax.get_xticklabels():
                tick.set_rotation(50)
            pval = pval*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            ax.set_title(looking_at + ": " + attribute + " pval: " + str(round(pval,2)),alpha=0.7)

        else:
            x = all_data_attribute[attribute].astype(float)
            y = all_data_attribute["catchment_least_square"]
            xy = pd.concat([x,y],axis=1)
            xy.dropna(inplace=True)
            results = scipy.stats.linregress(xy)           
            ax = sns.regplot(x,y, marker="o",
                        scatter_kws={"s":0.2, "facecolor":"lightsteelblue", "edgecolor":None},
                        line_kws={"color":"black", "linewidth":"0.75"})
            pval = results[3]*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval

            ax.set_title(looking_at + ": " + attribute + " pval: " +str(round(pval,2)),
                         alpha=0.7)
            ax.grid(True, color="lightgrey",zorder=0)

        ax.set_ylabel("Mean Least Square Error [/]",alpha=.7) 
        # Make nicer
        plt.setp(ax.get_yticklabels(), alpha=0.7)
        plt.setp(ax.get_xticklabels(), alpha=0.7)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        ax.set_xlabel(attribute, alpha=0.7)
        fig.tight_layout()
        plt.savefig(looking_at + attribute[:-4] + ".png", dpi=200)
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

    sns.heatmap(ls, square=True, cmap="Blues", yticklabels=False, xticklabels=1, 
                     cbar_kws = dict(use_gridspec=False,location="left",shrink= 0.3, pad=0.01), 
                     ax=ax_heatmap, linecolor="grey", linewidths=0.1)
    ax_heatmap.set_ylabel("Catchments", alpha=0.7)
    ax_heatmap.set_xlabel("Years", alpha=0.7)
    ax_heatmap.tick_params(axis=u'both', which=u'both',length=0)
    plt.setp(ax_heatmap.get_xticklabels(), alpha=0.7)
    
    cbar = ax_heatmap.collections[0].colorbar
    # here set the labelsize by 20
    cbar.ax.set_ylabel("Mean Least Square Error [/]", alpha=0.7)
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

    ax_bar_top.set_title("Yearly Mean of the Mean Least Square Error [/]", alpha=0.7)      
    ax_bar_right.set_ylabel("Catchment Mean of the Mean Least Square Error [/]", alpha=0.7, labelpad=-200, rotation=270)

    for tick in ax_bar_right.get_xticklabels():
        tick.set_rotation(90)     
    # Adjust top plot finely grained
    
    ax_bar_top.set_position([0.618,0.69, 0.175, 0.1])
    # Finishing touches    
    fig = plt.gcf()
    fig.set_size_inches(20,20)
    plt.savefig("heatmap_lse.png", dpi=800, bbox_inches="tight")
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
                        scatter_kws={"s":0.5, "facecolor":"steelblue", "edgecolor":"steelblue", "zorder":5, "alpha":0.5},
                        line_kws={"color":"black", "linewidth":"0.75", "zorder":6})
    results = scipy.stats.linregress(new.dropna())
    ax.set_title("Relationship Model Efficieny and Catchment Complexity, pval: " +str(round(results[3]*23,3)), alpha=0.7)
    ax.set_xlabel("Mean Least Square Error [/]", alpha=0.7)
    ax.set_ylabel("Kling Gupta Efficienty [/]", alpha=0.7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis=u'both', which=u'both',length=0)

    ax.grid(True, color="lightgrey", zorder=0)
    plt.setp(ax.get_yticklabels(), alpha=0.7)
    plt.setp(ax.get_xticklabels(), alpha=0.7)
    plt.savefig("kge_lse.png", dpi=200)
    plt.close()


if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments()
   
   years = ccdt.get_attributes_years()
   least_squares = pd.read_csv("least_square_all_catchments.csv", sep=";", index_col=0)
   del(least_squares["41510205"])
   heatmap_ls(least_squares)
#   scatter_violin_least_squares_attribute(catchments, least_squares, 0)
#   scatter_violin_least_squares_attribute(years, least_squares, 1)
#   scatter_violin_lse_all_together(catchments, years, least_squares)
 #  scatter_violin_lse_all_only_catchments(catchments, least_squares)
#   kge = pd.read_csv("kge_all_years_catch.csv", sep=";", index_col=0)
#   regplot_kge_lse(least_squares, kge)