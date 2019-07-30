# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 14:12:55 2019

@author: Florian Ulrich Jehn
"""
import pandas as pd
import os
# Get the location of this file
file_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.abspath(os.path.join(file_dir, os.pardir+os.sep))+os.sep+"cleaned_data")


def read_df(name):
    df = pd.read_csv(name, sep=";", index_col=0)
    df.index = pd.to_datetime(df.index)
    return df


def calculate_delta_s(dis, prec, et):
    """Calculates the storage change for all days"""
    dS = prec - dis - et
    return dS


et = read_df("et_mm_1991_2018.csv")
prec = read_df("prec_mm_1991_2018.csv")
dis = read_df("dis_mm_1991_2018.csv")
dS = calculate_delta_s(dis, prec, et)
dS.to_csv("dS_mm_1991_2018.csv", sep=";")