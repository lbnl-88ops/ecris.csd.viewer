from logging import getLogger
from pathlib import Path
from tkinter import filedialog
from typing import Any, List
import tkinter as tk

from csd_viewer.files.csd_file import CSDFile
from csd_viewer.gui.controls.controls import FileListControls, PlotControls
from csd_viewer.gui.controls.file_list import FileList
from csd_viewer.gui.info_frame.file_info_pane import FileInfoPane
from csd_viewer.gui import Plot, FileInfoPane
from csd_viewer.files.client import list_files, download_filepair

_log = getLogger(__name__)


class Coordinator:
    def __init__(self, objects: Any | List[Any]):
        if not isinstance(objects, List):
            objects = [objects]
        self.attach(objects)
        self.configure_objects()
        self.initialize()
        self.rescale_using_oxygen = tk.BooleanVar(value=True)

    def attach(self, objects: List[Any]) -> None:
        for object in objects:
            match object:
                case PlotControls():
                    self._plot_controls = object
                case FileInfoPane():
                    self._file_info_pane = object
                case FileList():
                    self._file_list = object
                case FileListControls():
                    self._file_list_controls = object
                case Plot():
                    self._plot = object
                case FileInfoPane():
                    self._file_info_pane = object
                case _:
                    raise RuntimeError(f"Coordinator passed bad object {object}")

    def configure_objects(self) -> None:
        self._file_list.file_listbox.bind("<<ListboxSelect>>", self.set_file_to_plot)
        self._file_list_controls.btRefresh.config(command=self.refresh_file_list)
        self._file_list_controls.btChangeDirectory.config(command=self.choose_directory)
        self._plot_controls.btClearPlot.config(command=self.clear_plot)
        self._plot_controls.btRemoveFromPlot.config(command=self.remove_from_plot)
        self._plot_controls.btViewCSD.config(command=self.plot_file)
        self._plot_controls.btAutoScale.config(command=self._plot.autoscale)
        self._plot_controls.set_button_status(True)

    def initialize(self) -> None:
        self.refresh_file_list()

    def choose_directory(self, *_):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self._file_list.current_directory = Path(new_directory)
            self._file_list.populate_listbox()
            self._file_list.update_label()

    def clear_plot(self, *_):
        for file in self._file_list.files:
            file.plotted = False
        self._file_list.clear_loaded()
        self._plot.clear_plot()
        self._file_list.update_colors()
        self._plot_controls.set_button_status(False)

    def plot_file(self):
        file = self._file_list.get_selected_file()
        if file is not None:
            csd_file = download_filepair(file)
            file = CSDFile(csd_file, 1)
            self._plot.plot(file, self.rescale_using_oxygen.get())
            # self._file_list.update_colors()
            # self._file_info_pane.update_info(file)
            self._plot_controls.set_button_status(True)

    def remove_from_plot(self, *_):
        file = self._file_list.get_selected_file()
        if file is not None:
            file.plotted = False
            file.unload_csd()
            self._plot.remove_file(file)
            self._file_list.update_colors()
            self._file_info_pane.update_info(file)
            self._plot_controls.set_button_status(False)

    def refresh_file_list(self, *_):
        files = list(reversed(sorted(list_files())))
        self._file_list.clear_loaded()
        self._file_list.fill_list_box(files)
        self._plot_controls.set_button_status(True)

    def set_file_to_plot(self, *_):
        file = self._file_list.get_selected_file()
        self._plot_controls.set_button_status(False)
