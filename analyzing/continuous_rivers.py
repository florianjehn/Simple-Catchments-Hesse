import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import seaborn as sns
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

        iterate = least_squares.index if axis == 1 else least_squares.columns
        collect = []
        for single_catch_year in iterate:
            if axis == 1:
                least_square_single = least_squares.loc[single_catch_year,:] 
            elif axis == 0:
                least_square_single = least_squares.loc[:,single_catch_year]
            least_square_single.name = "catchment_least_square"
            current_catch_att = catch_year.loc[int(single_catch_year), attribute]
            # Make attribute as long as the least squares
            current_catch_att = pd.Series([current_catch_att] * len(least_square_single), index=least_square_single.index)
            current_catch_att.name=attribute
            combined = pd.concat([least_square_single, pd.Series(current_catch_att)],axis=1)
         #   print(combined)
            collect.append(combined)
        all_data_attribute = pd.concat(collect,ignore_index=True)
        
        ax = plt.gca()
        fig = plt.gcf()

        if all_data_attribute[attribute].dtype != float:
            sns.violinplot(y="catchment_least_square", data=all_data_attribute, x=attribute,ax=ax)
        #    print(all_data_attribute[attribute])

        else:
            x = all_data_attribute[attribute].astype(float)
#            if x is None:
#                continue
            #print(x)
            y = all_data_attribute["catchment_least_square"]
            print(y)
            ax.scatter(x,y, s=0.1)
#            fit = np.polyfit(x,y , deg=2)
#            func = np.poly1d(fit)
#            y_sim = func(x)
#            ax.plot(x,y_sim, color="red")
            
        ax.set_title(attribute)
        ax.set_xlabel(attribute)
        ax.set_ylabel("least square error")
        fig.tight_layout()
        plt.savefig(attribute + ".png", dpi=150)
        plt.close()
        
    
    



if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   catchments = ccdt.get_attributes_catchments_num()
   years = ccdt.get_attributes_years()
   least_squares = pd.read_csv("least_square_all_catchments.csv", sep=";", index_col=0)
   
   scatter_violin_least_squares_attribute(catchments, least_squares, 0)