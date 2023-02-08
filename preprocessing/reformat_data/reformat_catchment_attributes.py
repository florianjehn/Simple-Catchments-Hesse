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
    att_df = pd.read_csv("all_catchment_attributes.csv", encoding='latin-1', sep=";", index_col=1)
    return att_df


def elongation_ratio(area_catchment, max_basin_length):
    """
    Calculates the elongation ration for a given catchment
    Watershed-based Morphometric Analysis: A Review S Sukristiyanti et al
    """
    diameter_catchment_circle = math.sqrt(area_catchment/math.pi) * 2
    return diameter_catchment_circle / max_basin_length


def calculate_elongation(att_df):
    """Calculate the elongation ratio for all catchments"""
    att_df["elongation_ratio"] = list(map(elongation_ratio, att_df["area_m2_watershed"], att_df["max_flow_len"]))
    return att_df


def calculate_yearly_means(att_df):
    for data_type in ["et", "dis", "prec"]:
        if data_type == "et":
            df = read_df(data_type+"_mm_1991_2018_corrected.csv")
        else:
            df = read_df(data_type+"_mm_1991_2018.csv")
        means = df.groupby(df.index.year).sum().mean()
        means.name = data_type + "_mean"
        means.index = means.index.astype(int)
        att_df = att_df.join(means)
    return att_df


def read_df(name):
    os.chdir(os.path.abspath(os.path.join(file_dir, os.pardir+os.sep))+os.sep+"cleaned_data")
    df = pd.read_csv(name, sep=";", index_col=0)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    return df


def remove_whitespace(data):
    for i in data.columns:
        # checking datatype of each columns
        if data[i].dtype == 'object':
            # applying strip function on column
            data[i] = data[i].map(str.strip)
    return data


def match_duplicates(data, col):
    """
    unique soil types are
    ['Dystric Cambisols', 'Eutric Cambisols / Stagnic Gleysols', 'Eutric Cambisols',
     'Haplic Luvisols / Eutric Podzoluvisols / Stagnic Gleysols', 'Spodic Cambisols', 'Spodic Cambisol']

     'Spodic Cambisols' is the same as 'Spodic Cambisol', so an additional 's' is needed
    """

    data[col] = np.where(data[col].str[-1] != "s", data[col] + "s", data[col])
    return data


# Get the data, add some and sort it
att_df = read_attributes()
att_df = calculate_elongation(att_df)
att_df = calculate_yearly_means(att_df)
att_df["runoff_ratio"] = att_df["dis_mean"] / att_df["prec_mean"]
# Only use categories
cleaned_cat = ['gauge', 
       'durchlässigkeit_huek250', 'dominating_soil_type_bk500',
       'land_use_corine',
       'area_m2_watershed_cat',
       'grundwasserneubildung_gwn_1000_cat',
       'greundigkeit_physgru_1000_cat',
       'slope_mean_dem_40_cat',  
       'elongation_ratio_cat', "et_mean_cat",
       "dis_mean_cat", "prec_mean_cat", "runoff_ratio_cat"]


cleaned_num = []
for item in cleaned_cat:
    if "cat" in item:
        cleaned_num.append(item[:-4])
    else:
        cleaned_num.append(item)


clean_att_df = att_df[cleaned_num].copy()
# remove redundant whitespace
clean_att_df = remove_whitespace(clean_att_df)
# make sure ever soil type ends with an "s" to prevent duplicates
clean_att_df = match_duplicates(clean_att_df, "dominating_soil_type_bk500")

# Go to the cleaned data folder
os.chdir(os.path.abspath(os.path.join(file_dir, os.pardir+os.sep))+os.sep+"cleaned_data")
# Save
clean_att_df.to_csv("cleaned_catchment_attributes_num.csv", sep=";")



