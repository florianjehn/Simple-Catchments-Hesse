# -*- coding: utf-8 -*-
"""
Created on Fri Aug 02 13:13:19 2019

@author: Florian Ulrich Jehn
Script for the computation of the hysteresis index by G. Zuecco (2016)
"""
import pandas as pd
import numpy as np


def hysteresis_class(x:pd.Series,y:pd.Series,x_fixed:pd.Series):
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
    rise_area,fall_area,diff_area,h = area_hysteresis_index(x_fixed, 
                                                            y_fixed_rise, 
                                                            y_fixed_fall)
    # Save the the min and max before forcing the linearity
    min_dA=min(diff_area)
    max_dA=max(diff_area)
    rise_area,fall_area,diff_area,h = force_linearity(rise_area,
                                                      fall_area, diff_area,h, 
                                                      x_fixed)
    return diff_area, h , find_hysteresis_class(x, y, min_dA, max_dA, h)


def normalize(series:pd.Series):
    return ((series-series.min()) / (series.max() - series.min()))


def find_independent_indices(x_fixed: pd.Series, x_norm:pd.Series):
    """
    The function indice_x_norm is applied to find indices for x for 
    observations for all values of x_fixed. 
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
    pos_max_x_norm = x_norm.index.get_loc(x_norm.idxmax())
    
    # Calculate the rising limb 
    delta_rise = pd.Series(np.nan, index=x_norm.index)
    for i in range(pos_max_x_norm + 1): # plus one as matlab counts different
        delta_rise.iloc[i] = x_norm.iloc[i] - x_selected
    # Lower than "0" = x_rise_minor
    if (delta_rise.dropna() > 0).all():
        x_rise_major = x_rise_minor = x_fall_major = x_fall_minor = np.nan
        return x_rise_major, x_rise_minor, x_fall_major, x_fall_minor
    
    # Find the negative value closest to 0
    value_negative = delta_rise[delta_rise<0].max()
    # Find the index of value_negative (latest occurence)
    index_value = delta_rise.where(
            delta_rise==value_negative).last_valid_index()
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
    for j in range(pos_max_x_norm, len(x_norm)):
        delta_fall[j] = x_norm[j] - x_selected
        
    # Hihger than "0" = x_fall_major
    # Find the positive value closest to 0
    value_positive = delta_fall[delta_fall>=0].min()
    # Find the index of value_positive (last occurence)
    index_value = delta_fall.where(
            delta_fall==value_positive).last_valid_index()
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
    m_rise=((y_norm[x_rise_h].values - y_norm[x_rise_l].values) / 
            (x_norm[x_rise_h].values - x_norm[x_rise_l].values)) 
    m_fall=((y_norm[x_fall_l].values - y_norm[x_fall_h].values) / 
            (x_norm[x_fall_l].values - x_norm[x_fall_h].values)) 
    # Calculate intercept for rising and falling limb
    q_rise=(((x_norm[x_rise_h].values * y_norm[x_rise_l].values) - 
             (x_norm[x_rise_l].values * y_norm[x_rise_h].values)) / 
             (x_norm[x_rise_h].values - x_norm[x_rise_l].values)) 
    q_fall=(((x_norm[x_fall_l].values * y_norm[x_fall_h].values) - 
             (x_norm[x_fall_h].values * y_norm[x_fall_l].values)) / 
             (x_norm[x_fall_l].values - x_norm[x_fall_h].values)) 
    
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



def area_hysteresis_index(x_fixed:pd.Series, y_fixed_rise:pd.Series, 
                          y_fixed_fall:pd.Series):
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
    
    for j in range(len(step)):
        step.iloc[j] = x_fixed[j+1] - x_fixed[j]
        areas_rising.iloc[j] = (y_fixed_rise[j+1] + y_fixed_rise[j]) * step[j] / 2
        areas_falling.iloc[j] = (y_fixed_fall[j+1] + y_fixed_fall[j]) * step[j] / 2
        diff_area.iloc[j] = areas_rising[j] - areas_falling[j]
    h = diff_area.sum()

    return areas_rising, areas_falling, diff_area,h


def force_linearity(rise_area:pd.Series, fall_area:pd.Series, 
                    diff_area:pd.Series, h: float, x_fixed:pd.Series):
    """not sure what this function is supposed to be doing"""
    # Forcing linearity (no loop) = 0
    for to_fix in [rise_area, fall_area, diff_area]:
        for k in range(len(x_fixed)-1):
            if np.isnan(to_fix[k]):
                to_fix[k] = 0
    if np.isnan(h):
        h=0
    return rise_area, fall_area, diff_area, h


def find_hysteresis_class(x:pd.Series, y:pd.Series, min_dA:float, 
                          max_dA:float, h:float):
    """
    Finds the hysteresis class based on the values calculated beforehand
    """
    pos_max_x = x.index.get_loc(x.idxmax())
    min_y_rise = min(y.iloc[:pos_max_x + 1])
    max_y_rise = max(y.iloc[:pos_max_x + 1])
    change_max_y_rise = abs(max_y_rise - y[0])
    change_min_y_rise = abs(min_y_rise - y[0])
    
    if change_max_y_rise > change_min_y_rise:
        if min_dA > 0 and max_dA > 0:
            hyst_class = 1
        else:
            if min_dA < 0 and max_dA < 0:
                hyst_class = 4
            else:
                if min_dA <= 0 and max_dA > 0 and h >= 0:
                    hyst_class = 2
                else:
                    if min_dA < 0 and max_dA >= 0 and h<0:
                        hyst_class = 3
                    else:
                        hyst_class = 0 # linearity
                
    if change_max_y_rise < change_min_y_rise:
        if min_dA > 0 and max_dA > 0:
            hyst_class = 5
        else:
            if min_dA < 0 and max_dA < 0:
                hyst_class = 8
            else:
                if min_dA <= 0 and max_dA > 0 and h >= 0:
                    hyst_class = 6
                else:
                    if min_dA < 0 and max_dA >= 0 and h < 0:
                        hyst_class= 7 
                    else:
                        hyst_class = 0 # linearity
    
    
    if change_max_y_rise == change_min_y_rise:
        pos_max_x = x.index.get_loc(x.idxmax())
        min_y_fall = min(y.iloc[pos_max_x:])
        max_y_fall = max(y.iloc[pos_max_x:])
        change_max_y_fall = abs(max_y_fall - y[0])
        change_min_y_fall = abs(min_y_fall - y[0])

        if change_max_y_fall > change_min_y_fall:
            if min_dA > 0 and max_dA > 0:
                hyst_class = 1
            else:
                if min_dA < 0 and max_dA < 0:
                    hyst_class = 4
                else:
                    if min_dA <= 0 and max_dA > 0 and h >= 0:
                        hyst_class = 2
                    else:
                        if min_dA < 0 and max_dA >= 0 and h < 0:
                            hyst_class = 3
                        else:
                            hyst_class = 0 # linearity
        else:
            if change_max_y_fall < change_min_y_fall:
                if min_dA > 0 and max_dA > 0:
                    hyst_class = 5
                else:
                    if min_dA < 0 and max_dA < 0:
                        hyst_class = 8
                    else:
                        if min_dA <= 0 and max_dA > 0 and h >= 0:
                            hyst_class = 6
                        else:
                            if min_dA < 0 and max_dA >= 0 and h < 0:
                                hyst_class = 7
                            else:
                                hyst_class = 0 # linearity

        if change_max_y_fall == change_min_y_fall:
            hyst_class = 0

    return hyst_class


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(nrows=4, ncols=2)
    mapping = {0:"soil_1", 1:"soil_2", 2:"connectivity_1", 3:"connectivity_2"}
    right_hyst_class = {"soil_1":4, "soil_2":1, "connectivity_1":0,
                        "connectivity_2":2}
    for sheet in range(4):
        print(mapping[sheet])
        test_df = pd.read_excel("hysteresis_examples.xlsx",
                                                   sheet_name=sheet, 
                                                   index_col=0)
        x = test_df[test_df.columns[0]]
        y = test_df[test_df.columns[1]]
        x_fixed = pd.Series([0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 
                             0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 
                             0.95, 1.00])
        diff_area, h, hyst_class = hysteresis_class(x, y, x_fixed)
        if hyst_class == right_hyst_class[mapping[sheet]]:
            print("Delivers same class for test data as matlab code")
        else:
            print("Delivers wrong hysteresis class")
        
        # make the same plots as the matlab code
        ax1 = axes[sheet, 0]
        ax2 = axes[sheet, 1]
        
        ax1.plot(x,y)
        ax1.set_xlabel("Streamflow")
        ax1.set_ylabel("Soil moisture")
        ax1.set_title('Hysteretic plot (input data)')
        
        x2 = [0, 0.5, 1]
        y2 = [0, 0, 0]
        
        ax2.plot(x_fixed[:-1], diff_area, color="red")
        ax2.set_xlabel('Streamflow (-)')
        ax2.set_ylabel('\DeltaA (-)')
        ax2.set_title('Difference between the integrals')
    
    fig.tight_layout()
    
    

