import pandas as pd
import os
import sys
import scipy
from scipy import stats
# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))
           
    
def calculate_p_values(catchments, obj_func):           
    """
    Calculates the p-values for the trends over the whole dataset. 
    """
    pval_df = pd.DataFrame(index=catchments.columns, columns=["Numerical Attribute", "Categorical Attribute"])
    for attribute in catchments.columns:
        # Prepare the data for statistics
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
            # Make attribute as long as the objective function
            current_catch_att = pd.Series([current_catch_att] * len(obj_func_single), index=obj_func_single.index)
            current_catch_att.name=attribute
            combined = pd.concat([obj_func_single, pd.Series(current_catch_att)],axis=1)
            collect.append(combined)
        all_data_attribute = pd.concat(collect,ignore_index=True)
        
        # Calculate the p-values
        bonferoni_p_val_correction = 23
        # Categorical Attribute
        if all_data_attribute[attribute].dtype != float:
            values_per_group = [col.dropna() for col_name, col in all_data_attribute.groupby(attribute)["catchment_obj_func"]]
            statistic, pval = scipy.stats.f_oneway(*values_per_group)
            pval = pval*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            pval = format_p_val(pval)
            pval_df.loc[attribute,"Categorical Attribute"] = pval
            print(pval)
        # Numerical Attributes
        else:           
            x = all_data_attribute[attribute].astype(float)
            y = all_data_attribute["catchment_obj_func"]
            xy = pd.concat([x,y],axis=1)
            xy.dropna(inplace=True)
            results = scipy.stats.linregress(xy)           
            pval = results[3]*bonferoni_p_val_correction
            pval = 1 if pval > 1 else pval
            pval = format_p_val(pval)
            pval_df.loc[attribute, "Numerical Attribute"] = pval
            print(pval)
            
    return pval_df
            
 
def format_p_val(pval):
    if pval > 0.01:
        return str(round(pval,3))
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
   years = ccdt.get_attributes_years()
   obj_func = pd.read_csv("obj_func_all_catchments.csv", sep=";", index_col=0)
   del(obj_func["41510205"])
   pval_df = calculate_p_values(catchments, obj_func)
   pval_df.to_csv("pvals.csv", sep=";")
