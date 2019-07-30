# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 12:49:49 2019

@author: Florian Ulrich Jehn
"""
import pandas as pd
from functools import reduce
import os
import datetime
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
            name, id_river = line.replace("\n","").split(";")
            mappings[id_river] = name
    return mappings            


def read_areas():
    """
    reads in the sizes of all catchments and returns them as a dict
    """
    os.chdir(file_dir)
    areas = {}
    with open("river_areas_m2.csv", "r") as catchments:
        # Skip the header
        catchments.readline()
        for catchment in catchments.readlines():
            gauge = catchment.split(";")[1]
            area = catchment.split(";")[2]
            areas[gauge] = float(area)
    return areas
               

def read_HLNUG_discharge(areas, mappings):
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
        river = pd.read_csv(file, index_col=0, skiprows=6, sep=" ", header=None,
                            na_values=-777)
        # Fix names and dates
        river.index = pd.to_datetime(river.index.map(str), format="%Y%m%d%H%M%S")
        river_id = file.split("_")[0]
        river.columns = [river_id]
        river.index.names = ["date"]
        # change unit
        gauge_name = mappings[river_id]
        river = m3_to_mm(river, areas[gauge_name])
        all_rivers.append(river)
    # Combine the dataframes
    discharge = reduce(lambda x, y: pd.merge(x, y, right_index=True, left_index=True), all_rivers)
    return discharge
    
    
def m3_to_mm(series, area):
    """
    Converts a series of m3 to mm
    """
    series = series * 86400 * 1000 / area
    return series   


def save_df(df, name):
    """
    saves a df in the cleaned data folder
    """
    # Go the the cleaned data folder
    os.chdir(os.path.abspath(os.path.join(file_dir, os.pardir+os.sep))+os.sep+"cleaned_data")
    # Save
    df.to_csv(name, sep=";")
        
    

    
start_date = datetime.date(1991, 1, 1)
end_date = datetime.date(2018, 12, 31)
mappings = read_mapping()
areas = read_areas()
discharge = read_HLNUG_discharge(areas, mappings)
discharge = discharge.loc[start_date:,:]
save_df(discharge, "discharge_mm_1991_2018.csv")
