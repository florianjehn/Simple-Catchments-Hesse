# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:13:19 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import os
import numpy as np
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


def classify_narrowness(att_df):
    """
    Classifies the narrowness of the catchments
    """
    att_df["ratio"] = att_df["laenge"] / att_df["breite"]
  #  att_df["narrowness"] = "equal_sided"
    # from https://stackoverflow.com/questions/44659040/pandas-assign-category-based-on-where-value-falls-in-range    
    def cat(x):
        if x > 1.2 and x < 1.4 or x < 0.8 and x > 0.6:
            return "narrow"
        if x > 1.4 or x < 0.6:
            return "very narrow"
        return "equal sided"

    att_df["narrowness"] = att_df["ratio"].apply(lambda x: cat(x))
    return att_df
    

att_df = read_attributes()
att_df = classify_narrowness(att_df)
att_df_classified = classify_numerical(att_df, 3, ["gauge_id", "breite", "laenge", "ratio"], ["lowest_third", "middle_third", "highest_third"])
