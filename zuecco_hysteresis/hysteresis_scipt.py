# -*- coding: utf-8 -*-
"""
Created on Fri Aug 02 13:13:19 2019

@author: Florian Ulrich Jehn
Script for the computation of the hysteresis index by G. Zuecco 
"""
import pandas as pd
import numpy as np

def normalize(values:pd.Series):
    """Normalizes a series"""
    return (values-values.min() / (values.max() - values.min()))


def indice_Qnorm(Qselected, Qnorm:pd.Series):
    """
    Zuecco G. - This function finds the indices for different values of the normalized Q (=discharge) 
    The script considers the selected discharge point (for example: 0.15, 0.30, 0.45,
    0.60, 0.75, 0.90). The output of the function are the observed limits for the selected discharge both
    in the rising and in the falling limb of the hydrograph. Qnorm represents the normalized discharge.
    """
    # Find the index of the streamflow peak
    maxQnorm = Qnorm.idxmax()
    
    # Calculate the rising limb of the hydrograph
    delta_rise = pd.Series(np.nan, index=Qnorm.index)
    for i in Qnorm.loc[:maxQnorm].index:
        # First part to find the closest values to Qselected
        delta_rise.loc[i] = abs(Qnorm.loc[i] - Qselected) 
    
    # Lower than "0" = Qrise_minor
    if (delta_rise > 0).all():
        Qrise_major = Qrise_minor = Qfall_major = Qfall_minor = np.nan
        return Qrise_major, Qrise_minor, Qfall_major, Qfall_minor

    # Find the negative value closest to 0
    value_negative = delta_rise[delta_rise<0].max()
    # Find the index of value_negative (latest occurence)
    index_value = delta_rise.where(delta_rise==value_negative).last_valid_index()
    index_position = delta_rise.index.get_loc(index_value)
    Qrise_minor = index_position
    
    # Higher than "0" = Qrise major
    if delta_rise.iloc[Qrise_minor+1] > delta_rise.iloc[Qrise_minor]:
        Qrise_major = Qrise_minor+1
    else:
        # Find closest value to Qselected in the upper part of the vector
        value_positive = delta_rise[delta_rise>0].min()
        # Select the closest value in time to the lower part of the vector
        # Find the index of value_negative (first occurence)
        index_value = delta_rise.where(delta_rise==value_positive).first_valid_index()
        index_position = delta_rise.index.get_loc(index_value)
        Qrise_major = index_position
        
    # Falling limb of the hydrograph
    delta_fall = pd.Series(np.nan, index=Qnorm.index)
    for j in Qnorm.loc[maxQnorm:].index:
        delta_fall[j] = Qnorm[j] - Qselected
        
    # Hihger than "0" = Qfall_major
    # Find the positive value closest to 0
    value_positive = delta_fall[delta_fall>0].min()
    # Find the index of value_positive (last occurence)
    index_value = delta_fall.where(delta_fall==value_positive).last_valid_index()
    index_position = delta_fall.index.get_loc(index_value)
    Qfall_major = index_position
    
    if Qfall_major == len(Qnorm):
        Qrise_major = Qrise_minor = Qfall_major = Qfall_minor = np.nan
        return Qrise_major, Qrise_minor, Qfall_major, Qfall_minor
    
    # Lower than "0" = Qfall_minor
    if (delta_fall > 0).all():
        Qrise_major = Qrise_minor = Qfall_major = Qfall_minor = np.nan
        return Qrise_major, Qrise_minor, Qfall_major, Qfall_minor
    
    if delta_fall.iloc[Qfall_major+1] < delta_fall.iloc[Qfall_major]:
        Qfall_minor = Qfall_major + 1
    else:
        # Find the negative value closest to 0
        value_negative = delta_fall[delta_fall<0].max()
        index_value = delta_fall.where(delta_fall==value_negative).last_valid_index()
        index_position = delta_fall.index.get_loc(index_value)        
        Qfall_minor = index_position   
    
    return Qrise_major, Qrise_minor, Qfall_major, Qfall_minor

if __name__ == "__main__":
    test_df = pd.read_excel("hysteresis_examples.xlsx", index_col=0)
    Q = test_df["Q"]
    y = test_df["soil_moisture"]
    Q_fixed = list(np.arange(0.15, 1.05, 0.05))
    Qnorm = normalize(Q)
    ynorm = normalize(y)