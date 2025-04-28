import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from ecris.csd.analysis.model import CSD

def plot_file(csd: CSD) -> Figure:
    fig = plt.figure(figsize=(9,6), tight_layout=True)
    ax = fig.gca()
    plt.plot(csd.m_over_q, csd.beam_current)
    ax.set_title(csd.timestamp)
    ax.set_xlabel('M/Q')
    ax.set_ylabel(r'current [$\mu$A]')
    return fig
