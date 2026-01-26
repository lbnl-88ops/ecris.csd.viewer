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

from ops.ecris.analysis.model.element import PERSISTANT_ELEMENTS, VARIABLE_ELEMENTS

from .coordinator import Coordinator, FileListType
from csd_viewer.gui.controls import ElementButtons
from csd_viewer.files.csd_file import CSDFile, export_to_file
from csd_viewer.files.configuration import (
    AppConfiguration,
    create_configuration,
    CONFIG_FILEPATH,
)
from csd_viewer.gui.style.patchMatplotlib import applyPatch
from csd_viewer.files.client import clear_temp_files
from csd_viewer.gui.status_pane import StatusPane
from csd_viewer.status_bar import StatusBarSingleton

from .gui import (
    Tools,
    FittingControls,
    FileList,
    PlotControls,
    Plot,
    FileListControls,
    AppMenu,
    DiagnosticWindow,
    FileInfoPane,
)


__version__ = "1.3.0-beta.1"

matplotlib.rc("font", size=14)
applyPatch()

logger = logging.getLogger("ops")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CSDViewer(ttk.Window):
    def __init__(self, configuration: AppConfiguration | None):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # self.geometry(f"{int(screen_width * 0.5)}x{int(screen_height * 0.5)}")
        # self.geometry("800x600")
        self.configuration = configuration
        if self.configuration is None:
            self.configuration = create_configuration()
        self.title(f"CSD Viewer (v{__version__})")
        self.pad = 5.0
        self.variable_elements = VARIABLE_ELEMENTS + self.configuration.custom_elements
        self.create_widgets()
        self.create_menu()
        self._info_visible = False
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

    def quit(self):
        clear_temp_files()
        self.plot.destroy()
        self.destroy()

    def create_menu(self):
        self.menu = AppMenu(
            self, self.plot.use_blitting, self.coordinator.rescale_using_oxygen
        )
        self.config(menu=self.menu)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.status_label = ttk.Label(
            self.status_bar,
            textvariable=StatusBarSingleton().get_status_var(),
            bootstyle="secondary",
            anchor=tk.W,
        )

        self.status_label.pack(side=tk.LEFT)

        self.plot = Plot(self.main_frame)
        self.control_pane = ttk.Frame(self.main_frame)
        # self.info_pane = FileInfoPane(self.main_frame)
        # self.btToggleFileInfo = ttk.Button(
        #     self.main_frame,
        #     textvariable=self.strToggleInfoText,
        #     command=self.info_pane.toggle_visibility,
        #     width=2,
        #     bootstyle="link-secondary",
        # )

        self.plot.pack(side="left", fill="both", expand=True)
        self.control_pane.pack(side="right", fill="y", expand=False)
        # self.btToggleFileInfo.pack(fill="y", side="left")

        self.status_pane = StatusPane(self.control_pane)
        self.file_list_pane = ttk.Frame(self.control_pane)

        self.file_list = FileList(self.file_list_pane)
        self.plotted_file_list = FileList(self.file_list_pane)

        self.element_buttons = ElementButtons(
            self.control_pane, self.plot, PERSISTANT_ELEMENTS, self.variable_elements
        )
        self.plot_controls = PlotControls(self.control_pane)
        self.fitting_controls = FittingControls(self.control_pane)
        self.tools = Tools(self.control_pane)

        self.plot.set_element_indicators(self.element_buttons.element_visibility)

        self.status_pane.pack()
        self.file_list_pane.pack()
        ttk.Label(self.file_list_pane, text="Available Files", justify="center").grid(
            row=0, column=0, sticky="n"
        )
        ttk.Label(self.file_list_pane, text="Plotted Files", justify="center").grid(
            row=0, column=1, sticky="n"
        )
        self.file_list.grid(row=1, column=0, sticky="n", padx=10, pady=(0, 10))
        self.plotted_file_list.grid(row=1, column=1, sticky="n", padx=10, pady=(0, 10))
        self.plot_controls.pack()
        self.fitting_controls.pack()
        self.tools.pack()
        self.element_buttons.pack(fill="both", padx=10, pady=10)
        self.strToggleInfoText = ttk.StringVar(value=">>")

        self.coordinator = Coordinator(
            self,
            [
                self.plot_controls,
                self.plot,
                self.fitting_controls,
                self.tools,
            ],
            self.configuration.default_directory,
        )
        self.coordinator.attach(self.file_list, FileListType.TO_PLOT)
        self.coordinator.attach(self.plotted_file_list, FileListType.PLOTTED)
        self.coordinator.attach(self.status_pane)
        self.coordinator.initialize()

    def export_data(self):
        # if len(self.plot.plotted_files()) > 1:
        # messagebox.showerror('Error', 'Can only export a single file. Please remove all but one datafile from the plot.')
        # return
        if len(self.plot.plotted_files()) == 0:
            messagebox.showerror("Error", "No plotted data to export.")
            return
        else:
            export_file = filedialog.asksaveasfile(
                title="Save exported data as",
                defaultextension=".csv",
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
                initialdir=self.configuration.default_directory,
            )
            if export_file is not None:
                try:
                    export_to_file(export_file, self.plot.plotted_files())
                    messagebox.showinfo("Success", "Export successful.")
                except ValueError as e:
                    messagebox.showerror("Error", f"Error exporting: {e}")

    def diagnostic_mode(self):
        self._diagnostic_window = DiagnosticWindow(self)

    def toggle_rescale(self):
        if not self.coordinator.rescale_using_oxygen.get():
            logging.info("Turning off oxygen rescaling")
            self.status_pane.strWarning.set("⚠️ Warning: Not rescaling!")
            self.status_pane.lblWarning.config(bootstyle="inverse-danger")
        else:
            logging.info("Turning on oxygen rescaling")
            self.status_pane.strWarning.set("")
            self.status_pane.lblWarning.config(bootstyle="danger")

    def toggle_blitting(self):
        logging.info(self.plot.use_blitting.get())
        if self.plot.use_blitting.get():
            if not messagebox.askokcancel(
                "Warning",
                """Activating blitting may cause some plot elements to not update automatically unless resized, are you sure you want to do this?""",
            ):
                self.plot.use_blitting.set(False)

    def _open_directory(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", path])
        else:
            messagebox.showerror(
                "Error", "Cannot open directory: unsupported operating system"
            )

    def open_config_directory(self):
        self._open_directory(CONFIG_FILEPATH)

    def open_data_directory(self):
        self._open_directory(self.default_path)
