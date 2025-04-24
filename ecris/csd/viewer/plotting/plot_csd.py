from logging import info
from matplotlib.lines import Line2D
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.artist import Artist
import datetime
from pathlib import Path
from typing import List, Tuple

from ecris.csd.viewer.files import CSDFile
from ecris.csd.viewer.analysis.m_over_q import estimate_m_over_q, rescale_with_oxygen

def plot_files(files: List[CSDFile]) -> Tuple[Figure, List[Artist]]:
    info(f'Plotting {len(files)}: {[str(f) for f in files]}')
    fig = Figure((9,6), tight_layout=True)
    ax = fig.gca()
    artists = []
    for file in files:
        artist = _plot_file(ax, file)
        if artist is not None:
            artists.append(artist)
    if len(files) > 1:
        ax.set_title('Multiple CSDs shown')
    elif len(files) > 0:
        ax.set_title(files[0].formatted_datetime)
    ax.set_xlabel('M/Q')
    ax.set_ylabel(r'current [$\mu$A]')
    return fig, artists

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
