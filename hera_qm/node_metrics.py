import os
import numpy as np
from pyuvdata import UVCal, UVData, utils
from hera_mc import cm_hookup

def calculate_correlation_matrix(sm,df,pols=['XX']):
    """Compute a metric of correlation for each baseline.

    The correlation is defined as:
        (even Vij) * conj(odd Vij)/(abs(even)*abs(odd))
    and then averaged over time and frequency.

    Parameters
    ----------
    sm : UVData
        UVData object from sum data file
    df: UVData
        UVData object from diff data file
    pols: list, optional
        List of strings representing polarization(s) to calculate metric on 
        (will accept any polarizations recognized by pyuvdata).
        Default is ['XX'].

    Returns
    -------
    corr_matrix : dict
        Dictionary of numpy arrays containing correlation metric for each baseline, 
        indexed by (pol, [ant1,ant2]).
    """
    if sm.time_array[0] != df.time_array[0]:
        print('FATAL ERROR: Sum and diff files are not from the same observation!')
        return None
    antnums = sort_antennas(sm)
    nants = len(antnums)
    corr_matrix = {}
    for p in range(len(pols)):
        pol = pols[p]
        corr_matrix[pol] = np.empty((nants,nants))
        for i in range(nants):
            for j in range(nants):
                ant1 = antnumsAll[i]
                ant2 = antnumsAll[j]
                s = sm.get_data(ant1,ant2,pol)
                d = df.get_data(ant1,ant2,pol)
                even = (s + d)/2
                even = np.divide(even,np.abs(even))
                odd = (s - d)/2
                odd = np.divide(odd,np.abs(odd))
                product = np.multiply(even,np.conj(odd))
                corr_matrix[pol][i,j] = np.abs(np.average(product))
    return corr_matrix