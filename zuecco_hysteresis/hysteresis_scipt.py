# -*- coding: utf-8 -*-
"""
Created on Fri Aug 02 13:13:19 2019

@author: Florian Ulrich Jehn
Script for the computation of the hysteresis index by G. Zuecco (2016)
"""
import pandas as pd
import numpy as np
from scipy.stats import linregress


def find_hysteresis_class(x:pd.Series,y:pd.Series,x_fixed:pd.Series):
    """
    Finds hysteresis class for x and y
    """
    x_norm = normalize(x)
    y_norm = normalize(y)
    x_rise_h, x_rise_l, x_fall_h, x_fall_l = find_independent_indices(x_fixed, 
                                                                      x_norm)
    check_for_error(x_fall_l, x_rise_l)
    y_fixed_rise, y_fixed_fall = y_for_x_fixed(x_rise_h, x_rise_l, 
                                               x_fall_h, x_fall_l, y_norm, 
                                               x_norm, x_fixed)
    print(y_fixed_rise)
    hysteresis_class = None
    return hysteresis_class


def normalize(series:pd.Series):
    return ((series-series.min()) / (series.max() - series.min()))


def find_independent_indices(x_fixed: pd.Series, x_norm:pd.Series):
    """
    The function indice_x_norm is applied to find indices for x for observations
    for all values of x_fixed. 
    """
    x_rise_h = pd.Series(0, index=range(len(x_fixed)))
    x_rise_l = pd.Series(0, index=range(len(x_fixed)))
    x_fall_h = pd.Series(0, index=range(len(x_fixed)))
    x_fall_l = pd.Series(0, index=range(len(x_fixed)))
    for k in range(len(x_fixed)):
        x_norm_list = list(x_norm)
        indices = [i for i, x in enumerate(x_norm_list) if x == x_fixed[k]]
        # check if indices is empty
        empty = not indices
        if empty:
            x_rise_h[k], x_rise_l[k], x_fall_h[k], x_fall_l[k] = (
                    indice_x_norm(x_fixed[k],x_norm))
        else:
            # Why save the same thing two times? Unclear in original script
            x_rise_h[k] = x_rise_l[k] = indices[0]
            x_fall_h[k] = x_fall_l[k] = indices[-1]           
            
    return x_rise_h, x_rise_l, x_fall_h, x_fall_l


def indice_x_norm(x_selected:float, x_norm:pd.Series):
    """
    This function finds the indices for different values of the independent 
    variable (x). The script considers the selected x_fixed point 
    (for example: 0.15, 0.30, 0.45, 0.60, 0.75, 0.90). The output of the 
    function are the observed limits for the selected x, both
    in the rising and in the falling limb of the hydrograph. 
    x_norm represents the normalized independent variable.
    """
    
    # Find the index of the peak
    index_max_x_norm = x_norm.index.get_loc(x_norm.idxmax())
    
    # Calculate the rising limb 
    delta_rise = pd.Series(np.nan, index=x_norm.index)
    for i in range(index_max_x_norm + 1): # plus one as matlab counts differently
        delta_rise.iloc[i] = x_norm.iloc[i] - x_selected
    # Lower than "0" = x_rise_minor
    if (delta_rise.dropna() > 0).all():
        x_rise_major = x_rise_minor = x_fall_major = x_fall_minor = np.nan
        return x_rise_major, x_rise_minor, x_fall_major, x_fall_minor
    
    # Find the negative value closest to 0
    value_negative = delta_rise[delta_rise<0].max()
    # Find the index of value_negative (latest occurence)
    index_value = delta_rise.where(delta_rise==value_negative).last_valid_index()
    index_position = delta_rise.index.get_loc(index_value)
    x_rise_minor = index_position
    # Higher than "0" = xrise major
    if delta_rise.iloc[x_rise_minor+1] > delta_rise.iloc[x_rise_minor]:
        x_rise_major = x_rise_minor+1
    else:
        # Find closest value to x_selected in the upper part of the vector
        value_positive = delta_rise[delta_rise>=0].min()
        # Select the closest value in time to the lower part of the vector
        # Find the index of value_negative (first occurence)
        index_value = delta_rise.where(
                delta_rise==value_positive).first_valid_index()
        index_position = delta_rise.index.get_loc(index_value)
        x_rise_major = index_position
        
    # Falling limb of the hydrograph
    delta_fall = pd.Series(np.nan, index=x_norm.index)
    for j in range(index_max_x_norm, len(x_norm)):
        delta_fall[j] = x_norm[j] - x_selected
        
    # Hihger than "0" = x_fall_major
    # Find the positive value closest to 0
    value_positive = delta_fall[delta_fall>=0].min()
    # Find the index of value_positive (last occurence)
    index_value = delta_fall.where(delta_fall==value_positive).last_valid_index()
    index_position = delta_fall.index.get_loc(index_value)
    x_fall_major = index_position
    
    if x_fall_major == len(x_norm):
        x_rise_major = x_rise_minor = x_fall_major = x_fall_minor = np.nan
        return x_rise_major, x_rise_minor, x_fall_major, x_fall_minor
    
    # Lower than "0" = x_fall_minor
    if (delta_fall.dropna() > 0).all():
        x_rise_major = x_rise_minor = x_fall_major = x_fall_minor = np.nan
        return x_rise_major, x_rise_minor, x_fall_major, x_fall_minor
    
    if delta_fall.iloc[x_fall_major+1] < delta_fall.iloc[x_fall_major]:
        x_fall_minor = x_fall_major + 1
    else:
        # Find the negative value closest to 0
        value_negative = delta_fall[delta_fall<0].max()
        index_value = delta_fall.where(
                delta_fall==value_negative).last_valid_index()
        index_position = delta_fall.index.get_loc(index_value)        
        x_fall_minor = index_position   
    return x_rise_major, x_rise_minor, x_fall_major, x_fall_minor
        

def check_for_error(x_fall_l:pd.Series, x_rise_l:pd.Series):
    """
    If variable check_Qfixed=1 --- Comment: if the error displays, the user 
    should understand that he/she should change the Q_fixed values
    discarding the smallest value
    """
    if x_fall_l.isnull().values.any() or x_rise_l.isnull().values.any():
        raise ValueError("""the independent variable, x, does not reach the 
                         minimum selected value in the rising and/or 
                         the falling curve""")


def y_for_x_fixed(x_rise_h:pd.Series, x_rise_l:pd.Series, x_fall_h:pd.Series, 
                  x_fall_l:pd.Series, y_norm:pd.Series, x_norm:pd.Series,
                  x_fixed:pd.Series):
    """
    Computation of slope and intercept to find the y values corresponding 
    to x_fixed
    """
    # Calculate the slope for rising and falling limb
    m_rise=(y_norm[x_rise_h].values - y_norm[x_rise_l].values) / (x_norm[x_rise_h].values - x_norm[x_rise_l].values) 
    m_fall=(y_norm[x_fall_l].values - y_norm[x_fall_h].values) / (x_norm[x_fall_l].values - x_norm[x_fall_h].values) 
    # Calculate intercept for rising and falling limb
    q_rise=((x_norm[x_rise_h].values * y_norm[x_rise_l].values) - (x_norm[x_rise_l].values * y_norm[x_rise_h].values)) / (x_norm[x_rise_h].values - x_norm[x_rise_l].values) 
    q_fall=((x_norm[x_fall_l].values * y_norm[x_fall_h].values) - (x_norm[x_fall_h].values * y_norm[x_fall_l].values)) / (x_norm[x_fall_l].values - x_norm[x_fall_h].values) 
    
    y_fixed_rise = pd.Series(0, index=x_fixed.index)
    y_fixed_fall = pd.Series(0, index=x_fixed.index)
    
    # Calculate the y values
    for k in range(len(x_fixed)):
        if np.isnan(m_rise[k]):
            y_fixed_rise.iloc[k] = y_norm[x_rise_h[k]]
        else:
            y_fixed_rise.iloc[k] = m_rise[k] * x_fixed[k] + q_rise[k]
        if np.isnan(m_fall[k]):
            y_fixed_fall.iloc[k] = y_norm[x_fall_h[k]]
        else:
            y_fixed_fall.iloc[k] = m_fall[k] * x_fixed[k] + q_fall[k]
            
    
    return y_fixed_rise, y_fixed_fall



def area_hysteresis_index(x_fixed:pd.Series, y_rising:pd.Series, y_falling:pd.Series):
    """
    Computation of the difference between integrals on the rising and the
    falling curve. The areas of trapezoid are computed because the functions
    are discontinuous
    """
    du = len(x_fixed) - 1
    step = pd.Series(0, index=range(du))
    areas_rising = pd.Series(0, index=range(du))
    areas_falling = pd.Series(0, index=range(du))
    diff_area = pd.Series(0, index=range(du))
    
    for j in len(step):
        step[j] = x_fixed[j+1] - x_fixed[j]
        areas_rising[j] = (y_rising[j+1] + y_rising[j]) * step[j] / 2
        areas_falling[j] = (y_falling[j+1] + y_falling[j]) * step[j] / 2
        diff_area[j] = areas_rising[j] - areas_falling[j]
    h = diff_area.sum()

    return areas_rising,areas_falling,diff_area,h




if __name__ == "__main__":
    test_df = pd.read_excel("hysteresis_examples.xlsx", index_col=0)
    x = test_df["Q"]
    y = test_df["soil_moisture"]
    x_fixed = pd.Series([0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60,
               0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00])
    hysteresis_class = find_hysteresis_class(x, y, x_fixed)

