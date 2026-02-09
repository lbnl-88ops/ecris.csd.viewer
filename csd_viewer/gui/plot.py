from logging import info, debug
import tkinter as tk
from typing import Dict, List
from pathlib import Path

from matplotlib.artist import Artist
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Cursor
from ..plotting.plot_csd import create_figure, plot_file, Rescale
from csd_viewer.files import CSDFile
from csd_viewer.plotting.element_indicators import (
    ElementIndicator,
    add_element_indicators,
)
from ops.ecris.analysis.model import Element


class Plot(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        tk.Frame.__init__(self, owner, relief=tk.RAISED, *args, **kwargs)
        self._is_empty = True
        self._bg = None
        self.element_indicators: List[ElementIndicator] = []
        self.draw_element_lines = tk.BooleanVar(value=False)
        self.use_blitting = tk.BooleanVar(value=False)
        self._file_artists: Dict[str, List[Artist]] = {}
        self.create_widgets()

    def create_widgets(self):
        self._figure = create_figure()
        self.canvas = FigureCanvasTkAgg(self._figure, master=self)
        self.canvas.mpl_connect("draw_event", self.on_draw)
        self.canvas.mpl_connect("resize_event", self.update)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        # self.canvas.get_tk_widget().pack()
        self.cursor = Cursor(
            self._figure.gca(), useblit=True, color="blue", linewidth=0.5
        )

    def set_element_indicators(self, elements: Dict[Element, tk.BooleanVar]):
        self.element_indicators = add_element_indicators(elements)

        self._figure.gca().set_prop_cycle(None)

    def add_element_indicator(
        self, element: Element, visibility_boolean: tk.BooleanVar
    ):
        self.element_indicators.extend(
            add_element_indicators({element: visibility_boolean})
        )

    def remove_element_indicator(self, element):
        for indicator in self.element_indicators:
            if indicator.element == element:
                indicator.element_artist.remove()
                indicator.marker_artist.remove()
                for label in indicator.label_artists:
                    label.artist.remove()
                self.element_indicators.remove(indicator)
                break

    def remove_file(self, file: Path):
        self._remove_files([file])

    def _remove_files(self, files: List[Path] | List[str]):
        ax = self.canvas.figure.gca()
        for to_remove in files:
            if isinstance(to_remove, Path):
                to_remove = to_remove.name
            try:
                artists = self._file_artists.pop(to_remove)
            except KeyError:
                info(f"Cannot remove file, not found: {to_remove}")
                info(self._file_artists)
                continue
            for a in artists:
                a.remove()
        if not self._file_artists:
            if ax.get_legend() is not None:
                ax.get_legend().remove()
            ax.set_prop_cycle(None)
        self.update()

    def clear_plot(self):
        self._remove_files(list(self._file_artists.keys()))

    def plot(self, file: CSDFile, rescaling_methods: List[Rescale]):
        debug(f"Plotting file {file.path}")
        artists = [
            a
            for a in [
                plot_file(self._figure.gca(), file, method)
                for method in rescaling_methods
            ]
            if a is not None
        ]
        if artists:
            debug("Artist was returned")
            self._file_artists[file.path.name] = artists
            self.update()

    def autoscale(self):
        ax = self._figure.gca()
        ax.relim(visible_only=True)
        ax.autoscale()
        ax.set_ybound(lower=0)
        self.update()

    def on_draw(self, event):
        self._bg = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self._draw_animated()

    def _draw_animated(self, rescale: bool = False):
        fig = self.canvas.figure
        ax = fig.gca()
        for artists in self._file_artists.values():
            for artist in artists:
                fig.draw_artist(artist)

        # Determine how many elements are visible
        visible_elements = [
            element for element in self.element_indicators if element.is_plotted
        ]
        y_min, y_max = ax.get_ylim()
        delta_y_height = 0.1 * abs(y_max - y_min)
        for i, element in enumerate(
            reversed(sorted(visible_elements, key=lambda e: len(e._m_over_q_values)))
        ):
            y_value = delta_y_height * (i + 1) + y_min
            element.draw(fig, y_value=y_value, lines=self.draw_element_lines.get())
        handles, labels = ax.get_legend_handles_labels()
        if handles and any(not l.startswith("_") for l in labels):
            ax.legend(handles, labels, fontsize=10)
        ax.set_ybound(lower=0)

    def update(self, *_):
        if self._bg is None:
            self.on_draw(None)
        else:
            self.canvas.restore_region(self._bg)
            self._draw_animated()
            if self.use_blitting.get():
                self.canvas.blit(self.canvas.figure.gca().clipbox)
            else:
                self.canvas.draw()
        self.canvas.flush_events()
