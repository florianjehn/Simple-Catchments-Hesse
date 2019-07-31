from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

def dQdt(Q: pd.Series):
    aQ = np.array(Q)
    dQ = aQ * np.NaN
    dQ[1:] = aQ[1:] - aQ[:-1]  # Use backward finite difference as a proxy for the derivate
    dQ[0] = dQ[1]  # Use forward finite difference for the first item
    return pd.Series(dQ, index=Q.index)


def plot_dQ_Q(Q: pd.Series):

    dQ = dQdt(Q)
    plt.loglog(Q[dQ < 0], -dQ[dQ < 0], '.')
    plt.xlabel('Discharge ($Q, mm day^{-1}$)')
    plt.ylabel(r'$-\frac{dQ}{dt} mm day^{-1}$')


def g(P: pd.Series, E: pd.Series, Q: pd.Series):
    """
    Calcuates the dQ/dS Catchment sensitivity function from catchment data
    Kirchner 2009, Eq. 18
    dQ/dt = dQ/dS*dS/dt = g(Q)*(P-E-Q) --> g(Q) = dQ/dt / (P - E - Q)
    """

    dQ = dQdt(Q)
    dS = P - E - Q
    return dQ / dS

