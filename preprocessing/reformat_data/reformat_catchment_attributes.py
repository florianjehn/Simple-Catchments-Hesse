# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:13:19 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
from functools import reduce
import os
import numpy as np
# Get the location of this file
file_dir = os.path.dirname(os.path.abspath(__file__))

def read_attributes():
    # Go to the directoy of the data
    # Three dirs up
    three_up = os.path.abspath(os.path.join(file_dir, os.pardir+os.sep+os.pardir+os.sep+os.pardir))
    # now locate raw data
    os.chdir(three_up+os.sep+"Rohdaten")
    # read
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

att_df = read_attributes()
df = classify_numerical(att_df, 3, ["gauge_id", "breite", "laenge"], ["lowest_third", "middle_third", "highest_third"])