from pathlib import Path
import tkinter as tk
from typing import List, Optional
from xml.dom.minidom import Element

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ..plotting.plot_csd import plot_files
from ecris.csd.viewer.files import CSDFile
from ecris.csd.viewer.plotting.element_indicators import add_element_indicators, PERSISTANT_ELEMENTS, Element

class Plot(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, relief=tk.RAISED, *args, **kwargs)
        self.canvas: FigureCanvasTkAgg | None = None
        self._plotted_files: List[CSDFile] = []
        self._bg = None
        self._figure = None
        self._csd_artists = None
        self._element_artists = None

    def plotted_files(self):
        return self._plotted_files

    def clear_plot(self):
        if self.canvas is not None:
            for widget in self.winfo_children():
                widget.destroy()

    def plot(self, file: CSDFile, elements: List[Element] = []):
        self.clear_plot()
        self._plotted_files.append(file)
        self._figure, self._csd_artists = plot_files(self._plotted_files)
        self._element_artists = add_element_indicators(PERSISTANT_ELEMENTS, self._figure)
        self.canvas = FigureCanvasTkAgg(self._figure, master=self)
        self.canvas.mpl_connect('draw_event', self.on_draw)
        self.canvas.mpl_connect('resize_event', self._update)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()
        print(self._csd_artists)

    def on_draw(self, event):
        self._bg = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self._draw_animated()

    def _draw_animated(self):
        fig = self.canvas.figure
        for a in self._csd_artists:
            fig.draw_artist(a)

        # Determine how many elements are visible
        ax = fig.gca()
        x_min, x_max = ax.get_xlim()
        visible_elements = [
            artist for artist in self._element_artists if 
            any(x_min < x < x_max for x in artist.get_xdata())
        ]
        for i, a in enumerate(visible_elements):
            y_min, y_max = ax.get_ylim()
            height = (i + 1)*(y_max + y_min)/len(visible_elements)/2
            a.set_ydata([height]*len(a.get_xdata()))
            fig.draw_artist(a)


    def _update(self, event):
        if self._bg is None:
            self.on_draw(None)
        else:
            self.canvas.restore_region(self._bg)
            self._draw_animated()
            self.canvas.blit(self.canvas.figure.bbox)
        self.canvas.flush_events()
        
        
        
    def on_resize(self, event):
        add_element_indicators(PERSISTANT_ELEMENTS, self.canvas.figure)