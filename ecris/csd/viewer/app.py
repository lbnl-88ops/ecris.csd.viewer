"""Main CSD Viewer App"""
from pathlib import Path
import tkinter as tk

from .files.file_list import FileList
from .plotting.plot import Plot
from .plot_controls import PlotControls

__version__ = "0.5.0"

class CSDViewer(tk.Tk):
    def __init__(self, default_path: Path):
        super().__init__()
        self.default_path = default_path.absolute()
        self.title(f"CSD Viewer (v{__version__})")
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        self.pad = 1.0
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        self.plot.destroy()
        self.destroy()

    def create_widgets(self):
        self.file_list = FileList(self.default_path)
        self.file_list.grid(row=0, column =1, padx=self.pad, pady=self.pad, sticky="nsew") 
        self.plot = Plot(self)
        self.plot.grid(row=0, column=0, padx=self.pad, pady=self.pad, sticky="nsew",
                       rowspan=2)
        self.controls = PlotControls(self.plot, self.file_list)
        self.controls.grid(row=1, column=1, padx=self.pad, pady=self.pad)