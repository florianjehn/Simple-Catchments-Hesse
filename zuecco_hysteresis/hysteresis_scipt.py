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
        delta_rise.loc[i] = abs(Qnorm.loc[i] - Qselected) # First part to find the closest values to Qselected
    
    # Lower than "0" = Qrise_minor
    negative = delta_rise[delta_rise<0]
    if len(negative) > 0:
        Qrise_major = Qrise_minor = Qfall_major = Qfall_minor = np.nan
        return Qrise_major, Qrise_minor, Qfall_major, Qfall_minor

    # 
    
    
    
    return Qrise_major, Qrise_minor, Qfall_major, Qfall_minor

if __name__ == "__main__":
    test_df = pd.read_excel("hysteresis_examples.xlsx", index_col=0)
    Q = test_df["Q"]
    y = test_df["soil_moisture"]
    Q_fixed = list(np.arange(0.15, 1.05, 0.05))
    Qnorm = normalize(Q)
    ynorm = normalize(y)