from enum import Enum, auto

from logging import info
from matplotlib.figure import Figure
from matplotlib.artist import Artist
from ops.ecris.analysis.csd.polynomial_fit import default_polynomial_fit
from ops.ecris.analysis.csd.m_over_q import estimate_m_over_q, scale_with_oxygen
from csd_viewer.files import CSDFile


class Rescale(Enum):
    NONE = auto()
    LINEAR = auto()
    POLYNOMIAL = auto()


def create_figure() -> Figure:
    fig = Figure((9, 6), tight_layout=True)
    ax = fig.gca()
    ax.set_xlabel("M/Q")
    ax.set_ylabel(r"current [$\mu$A]")
    ax.set_facecolor("white")
    return fig


def plot_file(ax, file: CSDFile, rescale_method=Rescale.NONE) -> Artist | None:
    csd = file.csd
    if csd is None:
        info(f"File object: {file.path} has no CSD.")
        return None

    match rescale_method:
        case Rescale.POLYNOMIAL:
            csd.m_over_q, sol = default_polynomial_fit(csd)
            info("Polynomial fit complete:")
            info(sol)
            label = file.formatted_datetime
        case Rescale.LINEAR:
            scale_with_oxygen(csd)
            label = file.formatted_datetime + " (linear scaling)"
        case Rescale.NONE:
            info("Skipping rescale")
            csd.m_over_q = estimate_m_over_q(csd)
            label = file.formatted_datetime + " (not rescaled)"

    (ln,) = ax.plot(csd.m_over_q, csd.beam_current, label=label, animated=True)
    return ln
