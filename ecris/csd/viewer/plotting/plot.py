from pathlib import Path
import tkinter as tk
from typing import List

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from .plot_csd import get_plot
from ecris.csd.viewer.files import CSDFile

class Plot(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, relief=tk.RAISED, *args, **kwargs)
        self.canvas = None
        self.plotted_files: List[CSDFile] = []

    def plotted_files(self):
        return self.plotted_files

    def clear_plot(self):
        if self.canvas is not None:
            for widget in self.winfo_children():
                widget.destroy()

    def plot(self, file: Path):
        self.plotted_files.append(file)
        self.clear_plot()
        self.canvas = FigureCanvasTkAgg(get_plot(file), master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()