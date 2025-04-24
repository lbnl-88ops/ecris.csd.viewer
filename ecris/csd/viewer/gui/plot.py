from logging import info
import tkinter as tk
from typing import Dict, List

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ..plotting.plot_csd import create_figure, file_artist
from ecris.csd.viewer.files import CSDFile
from ecris.csd.viewer.plotting.element_indicators import ElementIndicator, add_element_indicators
from ecris.csd.viewer.analysis import Element

class Plot(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        tk.Frame.__init__(self, owner, relief=tk.RAISED, *args, **kwargs)
        self._is_empty = True
        self._plotted_files: List[CSDFile] = []
        self._bg = None
        self.element_indicators: List[ElementIndicator] = []
        self.create_widgets()
        self.draw_element_lines = tk.BooleanVar(value=False)
        self.use_blitting = tk.BooleanVar(value=False)

    def create_widgets(self):
        self._csd_artists = []
        self._figure = create_figure()
        self.canvas = FigureCanvasTkAgg(self._figure, master=self)
        self.canvas.mpl_connect('draw_event', self.on_draw)
        self.canvas.mpl_connect('resize_event', self._update)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()

    def set_element_indicators(self, elements: Dict[Element, tk.BooleanVar]):
        self.element_indicators = add_element_indicators(elements, self._figure) 

    def add_element_indicator(self, 
                              element: Element, 
                              visibility_boolean: tk.BooleanVar):
        self.element_indicators.extend(add_element_indicators({element: visibility_boolean},
                                                              self._figure))

    def remove_element_indicator(self, element):
        for indicator in self.element_indicators:
            if indicator.element == element:
                indicator.element_artist.remove()
                indicator.marker_artist.remove()
                for label in indicator.label_artists:
                    label.artist.remove()
                self.element_indicators.remove(indicator)
                break

    def plotted_files(self):
        return self._plotted_files

    def clear_plot(self):
        ax = self.canvas.figure.gca()
        for artist in self._csd_artists:
            artist.remove()
        if ax.get_legend() is not None:
            ax.get_legend().remove()
        self._csd_artists = []
        ax.set_prop_cycle(None)
        self.update()

    def plot(self, file: CSDFile):
        artist = file_artist(self._figure.gca(), file)
        if artist is not None:
            self._csd_artists.append(artist)
            self.update()

    def autoscale(self):
        ax = self._figure.gca()
        ax.relim(visible_only=True)
        ax.autoscale()
        self.update()

    def on_draw(self, event):
        self._bg = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self._draw_animated()

    def _draw_animated(self, rescale: bool = False):
        fig = self.canvas.figure
        ax = fig.gca()
        for a in self._csd_artists:
            fig.draw_artist(a)

        # Determine how many elements are visible
        visible_elements = [element for element in 
                            self.element_indicators 
                            if element.is_visible(ax.get_xlim()) and element.is_plotted]
        y_min, y_max = ax.get_ylim()
        delta_y_height = 0.1*abs(y_max - y_min)
        for i, element in enumerate(reversed(sorted(visible_elements, 
                                                    key=lambda e: len(e.marker_artist.get_xdata())))):
            element.set_y_value(fig, delta_y_height*(i+1) + y_min, ax.get_ylim())
            element.set_x_scale(fig)
            element.draw(fig, lines=self.draw_element_lines.get())
        handles, labels = ax.get_legend_handles_labels()
        if handles and any(not l.startswith('_') for l in labels):
            ax.legend(handles, labels)

    def update(self):
        info(f'Updating plot: CSD artists: {len(self._csd_artists)}, element indicators: {len(self.element_indicators)}')
        self._update(None)

    def _update(self, event):
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
        
        
        
    # def on_resize(self, event):
        # add_element_indicators(PERSISTANT_ELEMENTS, self.canvas.figure)