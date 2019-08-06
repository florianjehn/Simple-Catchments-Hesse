# -*- coding: utf-8 -*-
"""
Created on Fri Aug 02 13:13:19 2019

@author: Florian Ulrich Jehn
Script for the computation of the hysteresis index by G. Zuecco 
"""
import pandas as pd
import numpy as np


if __name__ == "__main__":
    test_df = pd.read_excel("hysteresis_examples.xlsx", index_col=0)