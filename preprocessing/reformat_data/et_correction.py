import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def print_balance(df):
    """Prints the mean annual water balance"""
    values = {v: df[v].mean() * 365 for v in 'PEQ'}

    return 'P={P}, E={E} Q={Q} mm/a'.format(**values)


def ETcorrection(df: pd.DataFrame):
    """
    Calculates a ET correction factor to close the water balance of the catchments

    [citation needed]

    :param df: A dataframe of Catchment timeseries data
    :return:
    """
    totE = df.E.sum()  # total ET in mm over whole period

    balance = (df.P - df.E - df.Q).sum()  # water balance over whole period

    rel_diff = balance / totE  # water balance error relative to ET

    return rel_diff + 1  # Factor for ET

def corrected_ET(df: pd.DataFrame):

    fET = ETcorrection(df)
    return df.E * fET

def ETcorrection_all(dataframes: dict):
    """
    Calculates all ETcorrection factors for all catchments
    :param dataframes: A dict of all catchment dataframes
    :return: pd.Series
    """
    return pd.Series({k: ETcorrection(v) for k, v in dataframes.items()})

def plot_correction_effect(dataframes: dict):
    """Makes violin plots to compare corrected and uncorrected ET"""
    plt.violinplot([[dataframes[df].E.mean() * 365 for df in dataframes],
                [corrected_ET(df).mean() * 365 for df in dataframes]])


def plot_storage(dataframes: dict, attribs: pd.DataFrame):
    """
    Plots the storage development over the whole period
    :param dataframes:
    :param attributes:
    :return:
    """
    for catch in dataframes:
        df = dataframes[catch]
        fET = ETcorrection(df)
        print(catch, attribs.loc[catch].gauge, fET)
        plt.plot(np.cumsum(df.P - df.E * fET - df.Q), label=attribs.loc[catch].gauge)
        plt.ylabel('S(t) [mm]')

if __name__ == '__main__':
    import preprocessing.create_cleaned_data_table as ccdt
    dataframes = ccdt.get_table_dict()
    attribs = ccdt.get_attributes()
    plot_storage(dataframes, attribs)
    plt.show()
