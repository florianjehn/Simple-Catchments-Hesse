# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 10:58:50 2020

@author: Florian Jehn
"""
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

spi = pd.read_csv(".." + os.sep + "preprocessing" + os.sep + "cleaned_data" + os.sep + "spi_12_month.csv", sep=";")
spi["Date"] = pd.to_datetime(spi["Date"], format="%d.%m.%Y")
spi["Year"] = spi["Date"].dt.year
spi["Month"] = spi["Date"].dt.month
del spi["Date"]

spi_mad = spi.groupby("Year").mad()["Standardized Precipitation Index"]
min_spi = spi.groupby("Year").min()["Standardized Precipitation Index"]
max_spi = spi.groupby("Year").max()["Standardized Precipitation Index"]
range_spi = max_spi- min_spi
std_spi = spi.groupby("Year").std()["Standardized Precipitation Index"]
mean_spi = spi.groupby("Year").mean()["Standardized Precipitation Index"]


least_squares = pd.read_csv("least_square_all_catchments.csv", sep=";", index_col=0).mean(axis=1)
combine = pd.concat([spi_mad, range_spi, std_spi, mean_spi, min_spi, max_spi, least_squares], axis=1)
combine.columns = ["MAD", "RANGE","STD","MEAN", "MIN", "MAX","Least Squares"]

fig, axes = plt.subplots(nrows=2, ncols=3)
axes = axes.flatten()

for ax, col in zip(axes, combine.columns[:7]):
    sns.regplot(ax=ax, data=combine, y="Least Squares",x=col)
    rho, pval = spearmanr(combine[col], combine["Least Squares"])
    ax.set_title("cor: " + str(round(rho, 3)) +  "p_val: " + str(round(pval,3)))
    
fig.tight_layout()
    
    

