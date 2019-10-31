# -*- coding: utf-8 -*-
"""
Created on Thu Oct 02 13:13:19 2019

@author: Florian Ulrich Jehn
"""

import spotpy
from spotpy.examples.hymod_python.hymod import hymod
import pandas as pd
import os
import sys

# add the whole package to the path
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.sep.join(file_dir.split(os.sep)[:-1]))

def go_through_all_catch_years(dataframes):
    """
    Cycles through all catchments and years seperately and saves the KGE to
    a new dataframes (and then a csv)
    """
    kge_all_years_catch = pd.DataFrame(index=range(1992, 2019), columns = list(dataframes.keys()))
    for catch in dataframes.keys():
        for year, year_df in dataframes[catch].groupby("water_year"):
            if year_df.isnull().values.any():
                # Skip years with empty values
                continue
            mymodel= spot_setup(year_df.E, year_df.P, year_df.Q)
            sampler = spotpy.algorithms.lhs(mymodel,dbname="bla", dbformat="ram")
            sampler.sample(500)
            best = max(sampler.getdata()["like1"])
            kge_all_years_catch.loc[year, catch] = best
    kge_all_years_catch.to_csv("kge_all_years_catch.csv", sep=";")
            

            
            


class spot_setup(object):
    cmax  = spotpy.parameter.Uniform(low=1.0 , high=500,  optguess=250)
    bexp  = spotpy.parameter.Uniform(low=0.1 , high=2.0,  optguess=1)
    alpha = spotpy.parameter.Uniform(low=0.1 , high=0.99, optguess=0.5)
    Ks    = spotpy.parameter.Uniform(low=0.001 , high=0.10, optguess=0.05)
    Kq    = spotpy.parameter.Uniform(low=0.1 , high=0.99, optguess=0.5)
        
    def __init__(self, PET, Precip, trueObs):
        self.PET = PET
        self.Precip = Precip
        self.trueObs = trueObs
        
    def simulation(self,x):
        return hymod(self.Precip, self.PET, x[0], x[1], x[2], x[3], x[4])
        
    def evaluation(self):
        return self.trueObs
    
    def objectivefunction(self,simulation,evaluation, params=None):
        return spotpy.objectivefunctions.kge(evaluation, simulation)


if __name__ == "__main__":
   import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
   dataframes = ccdt.get_table_dict(calc_water_year=True, et_corrected=True)
   dataframes = {k: dataframes[k] for k in list(dataframes.keys())[:2]}
   go_through_all_catch_years(dataframes)
