from pathlib import Path
import tkinter as tk
from typing import List, Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ..plotting.plot_csd import plot_files, file_artist
from ecris.csd.viewer.files import CSDFile
from ecris.csd.viewer.plotting.element_indicators import add_element_indicators
from ecris.csd.viewer.analysis import Element

class Plot(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        tk.Frame.__init__(self, owner, relief=tk.RAISED, *args, **kwargs)
        self._plotted_files: List[CSDFile] = []
        self._bg = None
        self.element_indicators = None
        self.create_widgets()

    def create_widgets(self):
        self._figure, self._csd_artists = plot_files([])
        self.canvas = FigureCanvasTkAgg(self._figure, master=self)
        self.canvas.mpl_connect('draw_event', self.on_draw)
        self.canvas.mpl_connect('resize_event', self._update)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()
        self._orig_ylim = self._figure.gca().get_ylim()
        self._orig_xlim = self._figure.gca().get_xlim()

    def plotted_files(self):
        return self._plotted_files

    def clear_plot(self):
        ax = self.canvas.figure.gca()
        for artist in ax.get_lines():
            artist.remove()
        ax.legend().remove()
        ax.set_xlim(self._orig_xlim)
        ax.set_ylim(self._orig_ylim)
        self._csd_artists = []
        self.update()

    def plot(self, file: CSDFile):
        self._csd_artists.append(file_artist(self._figure.gca(), file))
        self.update()

    def on_draw(self, event):
        self._bg = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self._draw_animated()

    def _draw_animated(self):
        fig = self.canvas.figure
        ax = fig.gca()
        for a in self._csd_artists:
            fig.draw_artist(a)

        # # Determine how many elements are visible
        # visible_elements = [element for element in 
        #                     self.element_indicators 
        #                     if element.is_visible(ax.get_xlim()) and element.is_plotted]
        # for i, element in enumerate(visible_elements):
        #     element.set_y_limits(ax.get_ylim(), (i + 1)/len(visible_elements))
        #     element.set_x_scale(fig)
        #     a = element.marker_artist
        #     fig.draw_artist(a)
        #     for a in element.label_artists:
        #         fig.draw_artist(a)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles, labels)

    def update(self):
        self._update(None)

    def _update(self, event):
        if self._bg is None:
            self.on_draw(None)
        else:
            self.canvas.restore_region(self._bg)
            self._draw_animated()
            self.canvas.draw()
            # self.canvas.blit(self.canvas.figure.bbox)
        self.canvas.flush_events()
        
        
        
    # def on_resize(self, event):
        # add_element_indicators(PERSISTANT_ELEMENTS, self.canvas.figure)