from pathlib import Path
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from .plot_csd import get_plot

class Plot(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, relief=tk.RAISED, *args, **kwargs)
        self.canvas = None

    def plot(self, file: Path):
        if self.canvas is not None:
            for widget in self.winfo_children():
                widget.destroy()
        self.canvas = FigureCanvasTkAgg(get_plot(file), master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()