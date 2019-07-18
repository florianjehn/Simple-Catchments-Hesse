# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 12:49:49 2019

@author: gh2668
"""
import pandas as pd
import os

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
            
        
        
    


mappings = read_mapping()