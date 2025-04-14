import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import datetime
from pathlib import Path
from typing import List

from ecris.csd.viewer.files import CSDFile

alpha = 0.00824    # measured approximate relation between the dipole hall probe measure [tesla]
                   #    and M/Q: alpha = B_batman[tesla]/sqrt(M/Q * Vext[kV])

def getinfo(file: Path):
    """Read in datasheet and csd data pair: csd_? and dsht_?, where ? is a 10 digit epoch time int 

    Args:
        file (string): the csd file to be read in.  datasheet will be located using epoch time in name

    Returns:
        indices (int list): the list of indices in the datasheet file corresponding to different measures
        settings (float list): the values for the VENUS settings in the datasheet file
        names (string list): the list of names of the different VENUS settings
        data[:,0:4] (float array): csd information with four columns.  0: epoch time for each point in csd
             1: dipole current [A], 2: dipole field [tesla], 3: beam current [A]
    """
    data = np.loadtxt(file)
    with open(file.with_name(file.name.replace('csd', 'dsht')),'r') as f:
        dsht = f.readlines()
    indices = []
    settings = []
    names = []
    for a in dsht:
        a = a.split()
        indices.append(int(a[0]))
        settings.append(float(a[1]))
        names.append(a[2])
    return(indices,settings,names,data[:,0],data[:,1],data[:,2],data[:,3])

def estimateMoverQ(settings,names,bbatman):
    """Calculate estimate of csd M/Q array for csd scan

    Args:
        settings (float array): list of setting values from datasheet at start of csd
        names (string array): names of setting parameters from datasheet
        bbatman (float array): dipole magnetic field measured during csd
    
    Returns:
        M/Q calculated using "alpha" parameter measured previously, extraction voltage, and dipole field
    """

    index = names.index('extraction_v')       # find index where extraction voltage was recorded
    Vext = settings[index]                    # get extraction voltage setting for this CSD [kV]
    return bbatman*bbatman/alpha/alpha/Vext   # return float array giving estimate of M/Q using alpha
    

def interpolateMoverQ(MQest,ibeam,expectedpeaks,dpeak):
    """Find a few oxygen peaks in spectrum and try to correct M/Q array

    Args:
        MQest (float array): estimate of M/Q using measured alpha parameter
        ibeam (float array): beam current from CSD in amps
        expectedpeaks (float array): expected M/Q values where we should find peaks
        dpeak (float): how far away from an expected M/Q value we will look for the peak [unitless]

    Return:
        MQinterp (float array): the improved MQ array
        peaks (int array): the indices where the "expectedpeaks" peaks were found
    """

    expectedpeaks.sort()                # sort numerically.  Trouble if repeated values!??!
    peaks = []                          # track where peaks were located
    for MQpeak in expectedpeaks:
        istart = np.argmax(MQest>MQpeak-dpeak)
        iend = np.argmin(MQest<MQpeak+dpeak)
        peaks.append(istart+np.argmax(ibeam[istart:iend+1]))

    MQinterp = MQest*1.0                # start with estimate of M/Q as a base
    for i in range(len(peaks)):
        if i == 0:                      # rescale everything to the left of first peak
            MQinterp[:peaks[0]] = np.linspace(MQest[0],expectedpeaks[0],peaks[0])
        else:                           # sort peaks up to last peak
            MQinterp[peaks[i-1]:peaks[i]] = np.linspace(expectedpeaks[i-1],expectedpeaks[i],peaks[i]-peaks[i-1])
        # finally rescale everything to the right of last peak
        MQinterp[peaks[-1]:] = np.linspace(expectedpeaks[-1],MQest[-1],len(MQest)-peaks[-1])
    return(MQinterp,peaks)

def plot_files(files: List[CSDFile]) -> Figure():
    fig = Figure()
    ax = fig.gca()
    for file in files:
        _plot_file(ax, file)
    if len(files) > 1:
        ax.set_title('Multiple CSDs shown')
        ax.legend()
    else:
        ax.set_title(files[0].formatted_datetime)
    ax.set_xlabel('M/Q')
    ax.set_ylabel(r'current [$\mu$A]')
    return fig

def _plot_file(ax, file):
    indices, settings, names, tcsd, ibatman, bbatman, ibeam  = getinfo(file.path)
    MQest = estimateMoverQ(settings,names,bbatman)

    # these are the expected peaks that will be used to rescale M/Q plot
    #   Won't work if oxygen not there or really diminished!
    #   Don't repeat values as erratic behavior may result!
    expectedpeaks = [1.0,2.0,2.667, 3.2, 4.0, 5.333, 8.0]
    dpeak = .1
    MQinterp,peakinds = interpolateMoverQ(MQest,ibeam,expectedpeaks,dpeak)

    ax.plot(MQinterp,ibeam*1e6, label=file.formatted_datetime)
    #for i in range(len(peakinds)):
    #    plt.plot(expectedpeaks[i],ibeam[peakinds[i]]*1e6,'gx',label=r'$^{16}$O')
