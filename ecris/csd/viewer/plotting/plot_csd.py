from logging import info
from matplotlib.figure import Figure
from matplotlib.artist import Artist

from ecris.csd.viewer.files import CSDFile
from ecris.csd.analysis.m_over_q import estimate_m_over_q, rescale_with_oxygen

def create_figure() -> Figure:
    fig = Figure((9,6), tight_layout=True)
    ax = fig.gca()
    ax.set_xlabel('M/Q')
    ax.set_ylabel(r'current [$\mu$A]')
    return fig

def file_artist(axis, file: CSDFile) -> Artist | None:
    return _plot_file(axis, file)

def _plot_file(ax, file: CSDFile) -> Artist | None:
    csd = file.csd
    if csd is None:
        info(f'File {file.path} is invalid')
        return None
    csd.m_over_q = estimate_m_over_q(csd)
    rescale_with_oxygen(csd)
    ln, = ax.plot(csd.m_over_q, csd.beam_current, 
                  label=file.formatted_datetime, animated=True)
    return ln
