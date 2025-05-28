import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import ttkbootstrap as ttk

from .elements import ElementButtons
from .file_list import FileList
from ..plot import Plot
from ..info_frame.file_info_pane import FileInfoPane

class FileListControls(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.pad = 3.0
        self.create_widgets()

    def create_widgets(self):
        self.btChangeDirectory = ttk.Button(self, text="Choose directory", 
                                            style=ttk.PRIMARY)
        self.btRefresh = ttk.Button(self, text="Refresh file list", 
                                    style=ttk.PRIMARY + ttk.OUTLINE)
        for loc, widget in {
            (0, 0): self.btChangeDirectory, 
            (0, 1): self.btRefresh, 
            }.items():
            widget.grid(row=loc[0], column=loc[1], 
                        padx=self.pad, pady=self.pad, sticky='nsew')

class PlotControls(tk.Frame):
    def __init__(self, owner, plot: Plot, file_list: FileList, 
                 element_buttons: ElementButtons, 
                 info_pane: FileInfoPane, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.plot = plot
        self.info_pane = info_pane
        self.element_buttons = element_buttons
        self.pad = 3.0
        self.big_button_size = 2
        self.file_list = file_list
        self.create_widgets()
    
    def create_widgets(self):
        self.widgets = []
        self.btViewCSD = ttk.Button(self, text="Plot CSD",
                                  command=self.plot_file,
                                  bootstyle=(ttk.SUCCESS))
        self.btAutoScale = ttk.Button(self, text="Reset Scale",
                                     command=self.plot.autoscale,
                                     bootstyle=(ttk.SUCCESS, ttk.OUTLINE))
                                    #  height=self.big_button_size)
        self.btRemoveFromPlot = ttk.Button(self, text="Remove from plot",
                                           command=self.remove_from_plot,
                                           state=ttk.DISABLED,
                                           bootstyle=(ttk.OUTLINE, ttk.DANGER))
        self.btClearPlot = ttk.Button(self, text="Clear Plot", 
                                     command=self.clear_plot, 
                                     bootstyle=(ttk.OUTLINE))
        for loc, widget in {
            (0, 0): self.btViewCSD, 
            (0, 1): self.btAutoScale,
            (0, 2): self.btRemoveFromPlot,
            (0, 3): self.btClearPlot,
            }.items():
            widget.grid(row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky='nsew')

    def set_button_status(self, file_is_plotted=False):
        if file_is_plotted:
            self.btViewCSD.config(state='disabled')
            self.btRemoveFromPlot.config(state='enabled')
        else:
            self.btViewCSD.config(state='enabled')
            self.btRemoveFromPlot.config(state='disabled')

    def remove_from_plot(self):
        file = self.file_list.get_selected_file()
        if file is not None:
            self.plot.remove_file(file)
            self.file_list.update_colors()
            self.info_pane.update_info(file)
            self.set_button_status(False)

    def plot_file(self):
        file = self.file_list.get_selected_file()
        if file is not None:
            self.plot.plot(file)
            self.file_list.update_colors()
            self.info_pane.update_info(file)
            self.set_button_status(True)

    def clear_plot(self):
        self.plot.clear_plot()
        self.file_list.update_colors()

    def toggle_info_pane(self):
        self.info_pane.visible.set(not self.info_pane.visible.get())
