# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 12:49:49 2019

@author: gh2668
"""
import pandas as pd
from functools import reduce
import os
# Get the location of this file
file_dir = os.path.dirname(os.path.abspath(__file__))


def read_mapping():
    """
    Reads the mapping of the rivers to their id and returns it as a dict
    """
    # Make sure we are in the right directoy
    os.chdir(file_dir)
    mappings = {}
    with open("map_name_nr_pegel.csv", "r") as mapping:
        # Skip the header
        mapping.readline()
        for line in mapping.readlines():
            name, id_river = line.replace(" ", "").split(";")
            mappings[name] = id_river
    return mappings            
            

def read_HLNUG_discharge():
    """
    Reads the single discharge data of the HLNUG (https://www.hlnug.de/start.html)
    and returns it as a dataframe, where all values have the unit of mm (l/m²)
    and all rivers are contained in one file.
    """
    # Go to the directoy of the data
    # Three dirs up
    three_up = os.path.abspath(os.path.join(file_dir, os.pardir+os.sep+os.pardir+os.sep+os.pardir))
    # now locate raw data
    os.chdir(three_up+os.sep+"Rohdaten"+os.sep+"hessen_abfluss_von_hlnug")
    # Create an empty dataframe to fill
    all_rivers = []
    # Iterate over all rivers
    for file in os.listdir():
        # Skip all non data files
        if file[-3:] != "zrx":
            continue
        # Read in the river
        river = pd.read_csv(file, index_col=0, skiprows=6, sep=" ", header=None)
        # Fix names and dates
        river.index = pd.to_datetime(river.index.map(str), format="%Y%m%d%H%M%S")
        river.columns = [file.split("_")[0]]
        river.index.names = ["Date"]
        all_rivers.append(river)
    # Combine the dataframes
    discharge = reduce(lambda x, y: pd.merge(x, y, right_index=True, left_index=True), all_rivers)
#        print(type(river.index[0]))
#        river.index = pd.to_datetime(river.index, format=)
#        print(river)
#        print(file)
    return discharge
    
    


mappings = read_mapping()
discharge = read_HLNUG_discharge()