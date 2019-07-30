# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:13:19 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import os
import numpy as np
import math
# Get the location of this file
file_dir = os.path.dirname(os.path.abspath(__file__))

def read_attributes():
    att_df = pd.read_csv("all_catchment_attributes.csv", encoding='latin-1', sep=";")
    return att_df


def classify_numerical(df, bins, skip_cols, labels):
    """
    Classifies all numerical columns of a dataframe to a defined number of 
    classes and returns the new df
    """
    for col in df.columns:
        # Skyp all non numericals
        if not np.issubdtype(df[col], np.number) or col in skip_cols:
            continue
        df[col+"_cat"] = pd.cut(df[col], bins=bins, labels=labels)
    return df


def elongation_ratio(area_catchment, max_basin_length):
    """
    Calculates the elongation ration for a given catchment
    Watershed-based Morphometric Analysis: A Review S Sukristiyanti et al
    """
    diameter_catchment_circle = math.sqrt(area_catchment/math.pi) * 2
    return diameter_catchment_circle / max_basin_length

def height_difference(height_max, height_min):
    return height_max - height_min


def calculate_additional_measures(att_df):
    """Calculate the elongation ratio for all catchments"""
    att_df["elongation_ratio"] = list(map(elongation_ratio, att_df["area_m2_watershed"], att_df["max_flow_len"]))
    att_df["height_difference"] = list(map(height_difference, att_df["height_max"], att_df["height_min"]))
    return att_df
       

att_df = read_attributes()
att_df = calculate_additional_measures(att_df)

att_df = classify_numerical(att_df, 3, ["gauge_id", "breite", "laenge", "ratio", "max_flow_len", "perimeter"],
                                       ["lowest_third", "middle_third", "highest_third"])
cleaned = ['gauge', 'gauge_id', 'leitercharackter_huek250', 'hohlraumart_huek250',
       'durchlässigkeit_huek250', 'dominating_soil_type_bk500',
       'gesteinsart_huek250', 'soil_texture_boart_1000', 'land_use_corine',
       'bodenausgangsgesteine_bag5000', 'bodengrosslandschaft_bgl5000','area_m2_watershed_cat',
       'nFK_1m_FKD10dm_1000_cat', 'grundwasserneubildung_gwn_1000_cat',
       'sickerwasserrate_mean_swr_1000_cat', 'greundigkeit_physgru_1000_cat',
       'slope_mean_dem_40_cat', 'height_mean_dem_40_cat', 'height_min_cat',
       'height_max_cat', 'elongation_ratio_cat', 'height_difference_cat']
# Go the the cleaned data folder
os.chdir(os.path.abspath(os.path.join(file_dir, os.pardir+os.sep))+os.sep+"cleaned_data")
# Save
att_df[cleaned].to_csv("cleaned_attributes.csv", sep=";", index=False)



#def classify_narrowness(att_df):
#    """
#    Classifies the narrowness of the catchments
#    """
#    att_df["ratio"] = att_df["laenge"] / att_df["breite"]
#  #  att_df["narrowness"] = "equal_sided"
#    # from https://stackoverflow.com/questions/44659040/pandas-assign-category-based-on-where-value-falls-in-range    
#    def cat(x):
#        if x > 1.2 and x < 1.4 or x < 0.8 and x > 0.6:
#            return "narrow"
#        if x > 1.4 or x < 0.6:
#            return "very narrow"
#        return "equal sided"
#
#    att_df["narrowness"] = att_df["ratio"].apply(lambda x: cat(x))
#    return att_df