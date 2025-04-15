from pathlib import Path
import tkinter as tk
from typing import List

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ..plotting.plot_csd import plot_files
from ecris.csd.viewer.files import CSDFile

class Plot(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, relief=tk.RAISED, *args, **kwargs)
        self.canvas = None
        self._plotted_files: List[CSDFile] = []

    def plotted_files(self):
        return self._plotted_files

    def clear_plot(self):
        if self.canvas is not None:
            for widget in self.winfo_children():
                widget.destroy()

    def plot(self, file: CSDFile):
        self.clear_plot()
        self._plotted_files.append(file)
        self.canvas = FigureCanvasTkAgg(plot_files(self._plotted_files), master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()