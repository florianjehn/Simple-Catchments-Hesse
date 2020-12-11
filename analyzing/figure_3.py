# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 09:44:13 2019

@author: Florian Ulrich Jehn
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import math
import matplotlib.patches as patches


def create_data():
    """Create some random exponential data"""
    #np.random.seed(18)   
    pure = np.array(sorted([np.random.exponential() for i in range(10)]))
    noise = np.random.normal(0,1, pure.shape)
    signal = pure + noise
    return signal


def create_exponential_from_points(x,y):
    """Creates values corresponding to an exponential functino through the 
    scatter of x and y. Create a 100 points, so the curve is smooth"""
    x = np.array(x)
    x_new = np.linspace(x.min() - x.min(), x.max() + x.min(),100)
    optimal_parameters = find_exponential_function(x,y)
    y_sim = exponential(pd.DataFrame(x_new), *optimal_parameters)
    x_new = pd.Series(x_new)
    return x_new, y_sim


def find_exponential_function(x,y):
    """ Finds the best parameter values for an exponential function"""
    optimal_parameters, pcov = curve_fit(exponential, x, y)
    return optimal_parameters


def exponential(x,c, k):
    """
    Exponential Funktion
    """
    return c*math.e**(k*x)


def plot(signal_x, signal_y, exponential_x, exponential_y):
    """Plots that shit"""
    for df in [signal_x, signal_y, exponential_x, exponential_y]:
        df.reset_index(drop=True, inplace=True)
    ax =  plt.gca()
    # Draw points
    ax.plot(signal_x, signal_y, linestyle="", marker="o", color = "dimgrey", label="Measured Data")
    # Draw exponential function
    ax.plot(exponential_x, exponential_y, color="steelblue", label="Fitted Exponential Function")
    # Draw lines between exponential function and points
    df_exp = pd.DataFrame(exponential_y)
    df_exp.index = exponential_x
    df_sig = pd.DataFrame(signal_y)
    df_sig.index = [float(x) for x in signal_x]
    for i in df_sig.index:
        if i == 1.0:
            ax.plot([i,i], [df_sig.loc[i], df_exp.loc[i]], color="dimgrey", zorder=1, linestyle="--", label="Deviation")
        else:
            ax.plot([i,i], [df_sig.loc[i], df_exp.loc[i]], color="dimgrey", zorder=1, linestyle="--")
    # Draw the rectangles
#    for i in df_sig.index:
#        # Determine if the point is above or below the exponential function
#        dist_sig_exp = (df_sig.loc[i] - df_exp.loc[i]).values
#        below = True if dist_sig_exp < 0 else False
#        if below:
#            rect = patches.Rectangle(xy=(i, df_sig.loc[i]), width=abs(dist_sig_exp), height=abs(dist_sig_exp), facecolor="lightgrey",zorder=0, edgecolor="grey")
#        else:
#            rect = patches.Rectangle(xy=(i, df_exp.loc[i]), width=dist_sig_exp, height=dist_sig_exp, facecolor="lightgrey",zorder=0, edgecolor="grey")
#        ax.add_patch(rect)
        
        
    # Make it nice
    plt.setp(ax.get_yticklabels(), alpha=0)
    plt.setp(ax.get_xticklabels(), alpha=0)
    ax.tick_params(axis=u'both', which=u'both',length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(r"less    $\longleftarrow$    Storage    $\longrightarrow$    more", color="black", alpha=0.7)
    ax.set_ylabel(r"less    $\longleftarrow$    Discharge    $\longrightarrow$    more", color="black", alpha=0.7)
    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color("dimgrey")
    fig = plt.gcf()
    fig.tight_layout()
    fig.set_size_inches(5,10)
    # Save it
    plt.savefig("lse_example.png", dpi=200, bbox_inches="tight")
    plt.close()
    
            
def normalize(series:pd.Series):
    return ((series - series.min()) / (series.max() - series.min()))        
    
if __name__ == "__main__":
    signal = create_data()
    x = pd.Series([i + 1 for i in range(signal.shape[0])])
    y = pd.Series(signal)
    x_new, y_sim = create_exponential_from_points(x,y)
    plot(x,y, x_new, y_sim)
    
    
