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
    antnums = sm.antenna_numbers
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

def get_internode_correlations(sm,corr_matrix,pols=['XX']):
    """Compute the median internode correlation metric for each node.

    Parameters
    ----------
    sm : UVData
        UVData object from sum data file
    corr_matrix: dict
        Dictionary of numpy arrays containing correlation metric for each baseline, 
        indexed by (pol, [ant1,ant2]), as calculated by calculate_correlation_matrix().
    pols: list, optional
        List of strings representing polarization(s) to return internode medians for. 
        Must be contained in corr_matrix.
        Default is ['XX'].

    Returns
    -------
    nodeMeans : dict
        Dictionary of numpy arrays containing correlation metric for each baseline, 
        indexed by (node, 'inter' or 'intra', pol).
    """
    
    antnums=sm.antenna_numbers
    nants = len(antnums)
    nodes = get_nodes(antnums)
    nodeMeans = {}
    nodeCorrs = {}
    for node in nodes:
        nodeCorrs[node] = {
            'inter' : {},
            'intra' : {}
        }
        nodeMeans[node] = {
            'inter' : {},
            'intra' : {}
        }
        for pol in pols:
            nodeCorrs[node]['inter'][pol] = []
            nodeCorrs[node]['intra'][pol] = []
    for i in range(nants):
        for j in range(nants):
            ant1 = antnums[i]
            ant2 = antnums[j]
            if ant1 != ant2:
                key1 = 'HH%i:A' % (ant1)
                n1 = x[key1].get_part_in_hookup_from_type('node')['E<ground'][2]
                key2 = 'HH%i:A' % (ant2)
                n2 = x[key2].get_part_in_hookup_from_type('node')['E<ground'][2]
                for pol in pols:
                    dat = data[pol][i,j]
                    if n1 == n2:
                        nodeCorrs[n1]['intra'][pol].append(dat)
                        nodeCorrs[n2]['intra'][pol].append(dat)
                    else:
                        nodeCorrs[n1]['inter'][pol].append(dat)
                        nodeCorrs[n2]['inter'][pol].append(dat)
    for node in nodes:
        for pol in pols:
            nodeMeans[node]['inter'][pol] = np.nanmedian(nodeCorrs[node]['inter'][pol])
            nodeMeans[node]['intra'][pol] = np.nanmedian(nodeCorrs[node]['intra'][pol])
    return nodeMeans
    
def get_nodes(antnums):
    """Get a list of nodes included in the data.
    
    Parameters
    ----------
    antnums: list
        List of antenna numbers included in the data.

    Returns
    -------
    nodes : list
        List of nodes included in the data.
    """
    
    h = cm_hookup.Hookup()
    x = h.get_hookup('HH')
    nodes = []
    for ant in antnums:
        key = 'HH%i:A' % ant
        n = x[key].get_part_in_hookup_from_type('node')['E<ground'][2]
        if n in nodes:
            continue
        nodes.append(n)
    return nodes