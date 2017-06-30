import numpy as np
import aipy as a
from hera_cal import omni
import hera_qm.ant_metrics as ant_metrics

#Setup

verbose = True
plotFinalMetrics = False

pols = ['xx','xy','yx','yy']
JD = '2457757.47316'
dataFileDict = {}
for pol in pols:
    dataFileDict[pol] = '/data4/paper/HERA2015/'+JD.split('.')[0]+'/zen.'+JD+'.'+pol+'.HH.uvc' #works well    

freqs = np.arange(.1,.2,.1/1024)    
aa = a.cal.get_aa('hsa7458_v001', freqs)
info = omni.aa_to_info(aa, pols=[pols[-1][0]], crosspols=[pols[-1]])
reds = info.get_reds()

metricsJSONFilename = JD+'.metrics.json'


#Main script for computing and saving metrics

am = ant_metrics.Antenna_Metrics(dataFileDict, reds)
am.iterative_antenna_metrics_and_flagging(crossCut=5, deadCut=5, verbose=verbose)
am.save_antenna_metrics(metricsJSONFilename)


#Load results and plot them.

def plot_metric(metrics, ants=None, antpols=None, title='', ylabel='Modified z-Score', xlabel=''):
    '''Helper function for quickly plotting an individual antenna metric.'''

    if ants is None:
        ants = list(set([key[0] for key in metrics.keys()]))
    if antpols is None:
        antpols = list(set([key[1] for key in metrics.keys()]))
    
    plt.figure()    
    for antpol in antpols:
        for i,ant in enumerate(ants):
            metric = 0
            if metrics.has_key((ant,antpol)):
                metric = metrics[(ant,antpol)]
            plt.plot(i,metric,'.')
            plt.annotate(str(ant)+antpol,xy=(i,metrics[(ant,antpol)]))
        plt.gca().set_prop_cycle(None)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

metrics_results = ant_metrics.load_antenna_metrics(metricsJSONFilename)
if plotFinalMetrics:
    ant_metrics.plot_metric(metrics_results['final_mod_z_scores']['meanVij'], 
                            title = 'Mean Vij Modified z-Score')
    ant_metrics.plot_metric(metrics_results['final_mod_z_scores']['redCorr'],
                            title = 'Redundant Visibility Correlation Modified z-Score')
    ant_metrics.plot_metric(metrics_results['final_mod_z_scores']['meanVijXPol'], antpols=['x'],
                            title = 'Modified z-score of (Vxy+Vyx)/(Vxx+Vyy)')
    ant_metrics.plot_metric(metrics_results['final_mod_z_scores']['redCorrXPol'], antpols=['x'],
                            title = 'Modified z-Score of Power Correlation Ratio Cross/Same')