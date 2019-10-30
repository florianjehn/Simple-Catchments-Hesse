# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:19:33 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import datetime 
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
            name, id_river = line.replace("\n","").split(";")
            mappings[id_river] = name
    return mappings     


def read_averaged_data(data_type, data_name, mapping):
    """
    Reads in the averaged data from regnie and so on
    """
    # Go to the directoy of the data
    # Three dirs up
    three_up = os.path.abspath(os.path.join(file_dir, os.pardir+os.sep+os.pardir+os.sep+os.pardir))
    # now locate raw data
    os.chdir(three_up+os.sep+"Rohdaten"+os.sep+"database_1991-01-01_2019-04-30")
    all_data = pd.DataFrame()
    for file in os.listdir():
        if data_type not in file:
            continue
        name = file.split(".")[0] 
        temp_df = pd.read_csv(file, index_col=0)
        temp_df.index = pd.to_datetime(temp_df.index, format='%Y-%m-%d')
        # Handle the annoying German spelling
        split = name.split("_")            
        name = split[1] if len(split)==2 else " ".join(split[1:])
        if name.split(" ")[0] in ["Ober", "Nieder", "Unter", "Jossa"]:
            name = "-".join(name.split(" "))
        if name.split(" ")[0] == "Gross":
            split = name.split(" ")
            name = split[0] + "-" + split[1] + " " + split[2]
        print(name)
        temp_df.columns = [mapping[name]]
        all_data = pd.concat([all_data, temp_df], axis=1)
    return all_data  

def read_et(start_date, end_date, mapping):
    """
    Reads all actual et data for all catchments
    """
    return read_averaged_data("evapo_r", "ET",mapping).loc[start_date:end_date,:]

def read_prec(start_date, end_date, mapping):
    """
    Reads in the precipitation for all catchments
    """
    return read_averaged_data("regnie", "Prec", mapping).loc[start_date:end_date,:]

def read_soiltemp(start_date, end_date, mapping):
    return read_averaged_data("soil_temperature_5cm", "soil_temp_5cm", mapping).loc[start_date:end_date,:]
    

def save_df(df, name):
    """
    saves a df in the cleaned data folder
    """
    # Go the the cleaned data folder
    os.chdir(os.path.abspath(os.path.join(file_dir, os.pardir+os.sep))+os.sep+"cleaned_data")
    # Save
    df.to_csv(name, sep=";")
        

if __name__ == "__main__":
    # Save the cwd, so we can access it later to get back to the right path easier
    start_date = datetime.date(1991, 1, 1)
    end_date = datetime.date(2018, 12, 31)
    mapping = {v: k for k, v in read_mapping().items()}
    prec_df = read_prec(start_date, end_date, mapping)
    save_df(prec_df, "prec_mm_1991_2018.csv")
    temp_df = read_soiltemp(start_date, end_date, mapping)
    save_df(temp_df, "soil_temp_C_1991_2018.csv")
    # This creates only the uncorrected ET
#    et_df = read_et(start_date, end_date,mapping)
#    save_df(et_df, "et_mm_1991_2018.csv")

