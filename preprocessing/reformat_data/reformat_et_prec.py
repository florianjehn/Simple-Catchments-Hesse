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


def read_averaged_data(data_type, data_name):
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
        temp_df.index = pd.to_datetime(temp_df.index)
        temp_df.columns = [name]
        all_data = pd.concat([all_data, temp_df], axis=1)
    return all_data  

def read_et():
    """
    Reads all actual et data for all catchments
    """
    return read_averaged_data("evapo_r", "ET")  

def read_prec():
    """
    Reads in the precipitation for all catchments
    """
    return read_averaged_data("regnie", "Prec")   

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
    start_date = datetime.date(1991, 1, 7)
    end_date = datetime.date(2018, 12, 31)
    et_df = read_et()
    save_df(et_df, "et_mm_1991_2018.csv")
    prec_df = read_prec()
    save_df(prec_df, "prec_mm_1991_2018.csv")
