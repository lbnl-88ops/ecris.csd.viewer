from enum import Enum, auto

from logging import info
from matplotlib.figure import Figure
from matplotlib.artist import Artist
from ops.ecris.analysis.csd.polynomial_fit import polynomial_fit_mq, Element
from ops.ecris.analysis.csd.m_over_q import estimate_m_over_q, scale_with_oxygen
from csd_viewer.files import CSDFile
from csd_viewer.status_bar import update_status_bar


class Rescale(Enum):
    NONE = auto()
    LINEAR = auto()
    POLYNOMIAL = auto()


def create_figure() -> Figure:
    # fig = Figure((9, 6), tight_layout=True)
    fig = Figure()
    ax = fig.gca()
    ax.grid(alpha=0.5, ls="--")
    font_size = 10
    ax.tick_params(labelsize=font_size)
    ax.set_xticks(range(1, 11))
    ax.set_xlabel("M/Q", fontsize=font_size)
    ax.set_ylabel(r"current [$\mu$A]", fontsize=font_size)
    ax.set_facecolor("white")
    return fig


def plot_file(ax, file: CSDFile, rescale_method=Rescale.NONE) -> Artist | None:
    csd = file.csd
    if csd is None:
        info(f"File object: {file.path} has no CSD.")
        return None

    match rescale_method:
        case Rescale.POLYNOMIAL:
            csd.m_over_q, sol = polynomial_fit_mq(
                csd,
                [Element("O", "Oxygen", 15.9949, 8), Element("H", "Hydrogen", 1, 1)],
                polynomial_order=5,
                always_optimize=True,
            )
            info("Polynomial fit complete:")
            info(sol)
            if sol.success:
                update_status_bar("Polynomial fit succeeded.")
            else:
                update_status_bar(f"Polynomial fit failed: {sol.message}.")
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
