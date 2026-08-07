"""Main CSD Viewer App"""

import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk as ttk_main
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
    save_configuration,
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
from .gui.windows.vertical_scroll_frame import VerticalScrolledFrame


__version__ = "1.3.0-beta.4"

matplotlib.rc("font", size=14)
applyPatch()

logger = logging.getLogger("ops")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SplashScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Loading CSD Viewer...")
        self.geometry("400x150")
        self.resizable(False, False)
        # Center the splash screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        self.label = ttk.Label(self, text="Initializing...", font=("Helvetica", 12))
        self.label.pack(pady=20)
        
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=10)
        
        self.transient(master)
        self.grab_set()

    def update_progress(self, text, value):
        self.label.config(text=text)
        self.progress['value'] = value
        self.update()


class CSDViewer(ttk.Window):
    def __init__(self, configuration: AppConfiguration | None):
        super().__init__()
        self.withdraw()  # Hide immediately
        self.configuration = configuration
        if self.configuration is None:
            self.configuration = create_configuration()

        if (
            self.configuration.window_x is not None
            and self.configuration.window_y is not None
        ):
            self.geometry(
                f"{self.configuration.window_width}x{self.configuration.window_height}+{self.configuration.window_x}+{self.configuration.window_y}"
            )
        else:
            self.geometry(
                f"{self.configuration.window_width}x{self.configuration.window_height}"
            )

        self.title(f"CSD Viewer (v{__version__})")
        self.pad = 5.0
        self.variable_elements = VARIABLE_ELEMENTS + self.configuration.custom_elements
        self.create_widgets()
        self.create_menu()
        self._info_visible = False
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.update()
        self.minsize(800, 600)

        self.splash = SplashScreen(self)
        self.after(500, self.deferred_initialize)

    def deferred_initialize(self):
        try:
            self.coordinator.initialize(progress_callback=self.splash.update_progress)
            self.update()
            if self.configuration.sash_position is not None:
                try:
                    self.paned_window.sashpos(0, self.configuration.sash_position)
                except Exception as e:
                    logging.error(f"Error setting sash position: {e}")
            else:
                # Default to a reasonable split if no position is saved
                self.paned_window.sashpos(0, int(self.winfo_width() * 0.75))
        finally:
            self.splash.destroy()
            self.deiconify() # Show main window

    def quit(self):
        # Save geometry
        self.configuration.window_width = self.winfo_width()
        self.configuration.window_height = self.winfo_height()
        self.configuration.window_x = self.winfo_x()
        self.configuration.window_y = self.winfo_y()

        try:
            self.configuration.sash_position = self.paned_window.sashpos(0)
        except Exception as e:
            logging.error(f"Error getting sash position: {e}")

        save_configuration(self.configuration)

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
        self.paned_window = ttk.Panedwindow(
            self.main_frame,
            orient=tk.HORIZONTAL,
            # bootstyle="secondary",
        )

        self.paned_window.pack(fill=tk.BOTH, expand=True)
        ttk_main.Style().configure(
            "Sash",
            sashthickness=10,
            gripcount=4,
        )

        self.plot = Plot(self.paned_window)
        self.control_pane = VerticalScrolledFrame(self.paned_window)

        self.paned_window.add(self.plot, weight=3)
        self.paned_window.add(self.control_pane, weight=1)  # , minsize=400)
        # self.btToggleFileInfo.pack(fill="y", side="left")

        self.status_pane = StatusPane(self.control_pane.interior)
        self.file_list_pane = ttk.Frame(self.control_pane.interior)

        self.file_list = FileList(self.file_list_pane)
        self.plotted_file_list = FileList(self.file_list_pane)

        self.element_buttons = ElementButtons(
            self.control_pane.interior,
            self.plot,
            PERSISTANT_ELEMENTS,
            self.variable_elements,
        )
        self.plot_controls = PlotControls(self.control_pane.interior)
        self.fitting_controls = FittingControls(self.control_pane.interior)
        self.tools = Tools(self.control_pane.interior)

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

    def export_data(self):
        # if len(self.coordinator.plotted_files) > 1:
        # messagebox.showerror('Error', 'Can only export a single file. Please remove all but one datafile from the plot.')
        # return
        if len(self.coordinator.plotted_files) == 0:
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
                logging.info(f"Exporting data to {export_file.name}")
                with export_file:
                    try:
                        # Convert Paths to CSDFile objects for export
                        csd_files = [CSDFile(p, os.path.getsize(p)) for p in self.coordinator.plotted_files]
                        export_to_file(export_file, csd_files)
                        logging.info("Export successful")
                        messagebox.showinfo("Success", "Export successful.")
                    except ValueError as e:
                        logging.error(f"Error exporting: {e}")
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
        logging.info(f"Opening directory: {path}")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", path])
        else:
            logging.error(f"Cannot open directory {path}: unsupported operating system")
            messagebox.showerror(
                "Error", "Cannot open directory: unsupported operating system"
            )

    def open_config_directory(self):
        self._open_directory(CONFIG_FILEPATH)

    def open_data_directory(self):
        self._open_directory(self.configuration.default_directory)
