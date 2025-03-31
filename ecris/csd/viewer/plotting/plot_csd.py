import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import datetime
from pathlib import Path
from typing import List

from ecris.csd.viewer.files import CSDFile

alpha = 0.00824    # calculated...need notes DST

def getinfo(file: Path):
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
    index = names.index('extraction_v')
    Vext = settings[index]
    return bbatman*bbatman/alpha/alpha/Vext
    

def interpolateMoverQ(MQest,ibeam,expectedpeaks,dpeak):
    peaks = []
    for MQpeak in expectedpeaks:
        istart = np.argmax(MQest>MQpeak-dpeak)
        iend = np.argmin(MQest<MQpeak+dpeak)
        peaks.append(istart+np.argmax(ibeam[istart:iend+1]))

    MQinterp = MQest*1.0
    for i in range(len(peaks)):
        if i == 0:
            MQinterp[:peaks[0]] = np.linspace(MQest[0],expectedpeaks[0],peaks[0])
        elif i<len(peaks)-1:
            MQinterp[peaks[i-1]:peaks[i]] = np.linspace(expectedpeaks[i-1],expectedpeaks[i],peaks[i]-peaks[i-1])
        else:
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
    expectedpeaks = [1.0,2.0,2.667, 3.2, 4.0, 5.333, 8.0]
    dpeak = .1
    MQinterp,peakinds = interpolateMoverQ(MQest,ibeam,expectedpeaks,dpeak)

    ax.plot(MQinterp,ibeam*1e6, label=file.formatted_datetime)
    #for i in range(len(peakinds)):
    #    plt.plot(expectedpeaks[i],ibeam[peakinds[i]]*1e6,'gx',label=r'$^{16}$O')
