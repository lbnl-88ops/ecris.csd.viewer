"""Main CSD Viewer App"""
from pathlib import Path
import tkinter as tk

from ecris.csd.viewer.gui.elements import ElementButtons

from .gui import FileList, PlotControls, Plot
from .analysis.element import PERSISTANT_ELEMENTS, VARIABLE_ELEMENTS

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
        self.plot = Plot(self, PERSISTANT_ELEMENTS + VARIABLE_ELEMENTS)
        self.plot.grid(row=0, column=0, padx=self.pad, pady=self.pad, sticky="nsew",
                       rowspan=3)
        self.element_buttons = ElementButtons(self, self.plot)
        self.element_buttons.grid(row=1, column=1, padx=self.pad, pady=self.pad)
        self.controls = PlotControls(self.plot, self.file_list, self.element_buttons)
        self.controls.grid(row=2, column=1, padx=self.pad, pady=self.pad)