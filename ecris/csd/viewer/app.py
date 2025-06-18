"""Main CSD Viewer App"""
import logging
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import matplotlib
import platform
import os
import subprocess

import ttkbootstrap as ttk

from ecris.csd.analysis import PERSISTANT_ELEMENTS, VARIABLE_ELEMENTS

from ecris.csd.viewer.gui.elements import ElementButtons
from ecris.csd.viewer.files.csd_file import export_to_file
from ecris.csd.viewer.files.configuration import AppConfiguration, create_configuration, CONFIG_FILEPATH
from ecris.csd.viewer.gui.style.patchMatplotlib import applyPatch

from .gui import FileList, PlotControls, Plot, FileListControls, AppMenu, DiagnosticWindow, FileInfoPane


__version__ = "1.2.0-beta.2"

matplotlib.rc('font', size=14)
applyPatch()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CSDViewer(ttk.Window):
    def __init__(self, configuration: AppConfiguration | None):
        super().__init__()
        self.configuration = configuration
        if self.configuration is None:
            self.configuration = create_configuration()
        self.default_path = self.configuration.default_directory
        self.title(f"CSD Viewer (v{__version__})")
        self.pad = 5.0
        self.variable_elements = VARIABLE_ELEMENTS + self.configuration.custom_elements
        
        self.create_widgets()
        self.create_menu()
        self._info_visible = False
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        self.plot.destroy()
        self.destroy()

    def create_menu(self):
        self.menu = AppMenu(self, self.plot.use_blitting)
        self.config(menu=self.menu)

    def create_widgets(self):

        self.plot = Plot(self) 

        self.center_pane = ttk.Frame(self)

        self.info_pane = FileInfoPane(self)
        self.file_list = FileList(self.center_pane, self.info_pane, self.default_path)
        self.file_list_controls = FileListControls(self.center_pane, self.file_list)
        self.element_buttons = ElementButtons(self.center_pane, self.plot, PERSISTANT_ELEMENTS, self.variable_elements)
        self.controls = PlotControls(self.center_pane, self.plot, self.file_list, self.element_buttons,
                                     self.info_pane)

        self.plot.set_element_indicators(self.element_buttons.element_visibility)

        self.plot.pack(side='left', fill='both', expand=True)

        self.center_pane.pack(side='left', fill='y', expand=True)

        self.file_list_controls.pack()
        self.file_list.pack(padx=10, pady=10)
        self.controls.pack()
        self.element_buttons.pack(fill="both", padx=10, pady=10)
        self.strToggleInfoText = ttk.StringVar(value='>>')
        self.btToggleFileInfo = ttk.Button(self, textvariable=self.strToggleInfoText,
                                           command=self.info_pane.toggle_visibility,
                                           width=2,
                                           bootstyle=ttk.LINK + ttk.SECONDARY)
        self.btToggleFileInfo.pack(fill='y', side='left')

    def export_data(self):
        # if len(self.plot.plotted_files()) > 1:
            # messagebox.showerror('Error', 'Can only export a single file. Please remove all but one datafile from the plot.')
            # return
        if len(self.plot.plotted_files()) == 0:
            messagebox.showerror('Error', 'No plotted data to export.')
            return
        else:
            export_file = filedialog.asksaveasfile(title='Save exported data as', 
                                                   defaultextension='.csv', 
                                                   filetypes=(("CSV files", "*.csv"), 
                                                              ("All files", "*.*")), 
                                                   initialdir=self.configuration.default_directory)
            if export_file is not None:
                try:
                    export_to_file(export_file, self.plot.plotted_files())
                    messagebox.showinfo('Success', 'Export successful.')
                except ValueError as e:
                    messagebox.showerror('Error', f'Error exporting: {e}')

    def diagnostic_mode(self):
        self._diagnostic_window = DiagnosticWindow(self)

    def toggle_blitting(self):
        logging.info(self.plot.use_blitting.get())
        if self.plot.use_blitting.get():
            if not messagebox.askokcancel('Warning', """Activating blitting may cause some plot elements to not update automatically unless resized, are you sure you want to do this?"""):
                self.plot.use_blitting.set(False)

    def _open_directory(self, path):
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", path])
        else:
            messagebox.showerror('Error', 'Cannot open directory: unsupported operating system')

    def open_config_directory(self):
        self._open_directory(CONFIG_FILEPATH)

    def open_data_directory(self):
        self._open_directory(self.default_path)