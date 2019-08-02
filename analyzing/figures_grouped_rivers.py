# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 11:44:42 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import matplotlib as mpl
import matplotlib.patches as mpatches


def read_data(name)



def create_color_lookup(unique_attributes):
    """
    Creates a lookup table for the different attributes
    """
    color_lookup = {}
    colors = sns.color_palette("terrain", len(unique_attributes))
    for att, color in zip(unique_attributes, colors):
        color_lookup[att] = color
    return color_lookup