import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import ttkbootstrap as ttk

from ecris.csd.viewer.gui.elements import ElementButtons

from .file_list import FileList
from .plot import Plot

class FileListControls(tk.Frame):
    def __init__(self, owner, file_list: FileList, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.pad = 3.0
        self.big_button_size = 2
        self.file_list = file_list
        self.create_widgets()

    def create_widgets(self):
        self.widgets = []
        self.btChangeDirectory = ttk.Button(self, text="Choose directory", 
                                            command=self.choose_directory,
                                            bootstyle=ttk.PRIMARY)
        self.btRefresh = ttk.Button(self, text="Refresh file list", 
                                 command=self.refresh,
                                 bootstyle=(ttk.PRIMARY, ttk.OUTLINE))
        for loc, widget in {
            (0, 0): self.btChangeDirectory, 
            (0, 1): self.btRefresh, 
            }.items():
            widget.grid(row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky='nsew')

    def choose_directory(self):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self.file_list.current_directory = Path(new_directory)
            self.file_list.populate_listbox()
            self.file_list.update_label()

    def refresh(self):
        self.file_list.populate_listbox(retain_plotted=True)

class PlotControls(tk.Frame):
    def __init__(self, owner, plot: Plot, file_list: FileList, 
                 element_buttons: ElementButtons, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.plot = plot
        self.element_buttons = element_buttons
        self.pad = 3.0
        self.big_button_size = 2
        self.file_list = file_list
        self.create_widgets()
    
    def create_widgets(self):
        self.widgets = []
        self.btViewCSD = ttk.Button(self, text="Plot CSD",
                                  command=self.plot_file,
                                #   height=self.big_button_size,
                                  bootstyle=(ttk.SUCCESS))
        self.btAutoScale = ttk.Button(self, text="Reset Scale",
                                     command=self.plot.autoscale,
                                     bootstyle=(ttk.SUCCESS, ttk.OUTLINE))
                                    #  height=self.big_button_size)
        self.btClearPlot = ttk.Button(self, text="Clear Plot", 
                                     command=self.clear_plot, 
                                     bootstyle=(ttk.OUTLINE))
                                    #  height=self.big_button_size)
        self.btShowFileInfo = ttk.Button(self, text="File Info",
                                         command=self.toggle_info_pane,
                                         bootstyle=(ttk.SUCCESS, ttk.OUTLINE))
        for loc, widget in {
            (0, 0): self.btViewCSD, 
            (0, 1): self.btShowFileInfo,
            (0, 2): self.btAutoScale,
            (0, 3): self.btClearPlot,
            }.items():
            widget.grid(row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky='nsew')

    def plot_file(self):
        file = self.file_list.get_selected_file()
        if file is not None:
            self.plot.plot(file)
            self.file_list.update_colors()

    def clear_plot(self):
        self.plot.clear_plot()
        self.file_list.update_colors()

    def toggle_info_pane(self):
        self._owner.toggle_info_pane()
