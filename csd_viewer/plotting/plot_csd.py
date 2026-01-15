from logging import info
from matplotlib.figure import Figure
from matplotlib.artist import Artist

from ops.ecris.analysis.csd.m_over_q import estimate_m_over_q, scale_with_oxygen
from csd_viewer.files import CSDFile


def create_figure() -> Figure:
    fig = Figure((9, 6), tight_layout=True)
    ax = fig.gca()
    ax.set_xlabel("M/Q")
    ax.set_ylabel(r"current [$\mu$A]")
    ax.set_facecolor("white")
    return fig


def plot_file(ax, file: CSDFile, rescale) -> Artist | None:
    csd = file.csd
    if csd is None:
        info(f"File object: {file.path} has no CSD.")
        return None

    if rescale:
        scale_with_oxygen(csd)
        label = file.formatted_datetime
    else:
        info("Skipping oxygen rescale")
        csd.m_over_q = estimate_m_over_q(csd)
        label = file.formatted_datetime + " (not rescaled)"

    (ln,) = ax.plot(csd.m_over_q, csd.beam_current, label=label, animated=True)
    return ln
