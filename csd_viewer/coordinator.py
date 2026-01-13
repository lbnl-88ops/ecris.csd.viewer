from enum import Enum, auto
from logging import getLogger
from pathlib import Path
from tkinter import filedialog
from typing import Any, List, Optional
import tkinter as tk

from csd_viewer.files.csd_file import CSDFile
from csd_viewer.gui.controls.controls import FileListControls, PlotControls
from csd_viewer.gui.controls.file_list import FileList
from csd_viewer.gui.info_frame.file_info_pane import FileInfoPane
from csd_viewer.gui import Plot, FileInfoPane
from csd_viewer.files.client import list_files, download_filepair, clear_temp_files

_log = getLogger(__name__)


class FileListType(Enum):
    TO_PLOT = auto()
    PLOTTED = auto()


class Coordinator:
    def __init__(self, objects: Any | List[Any]):
        if not isinstance(objects, List):
            objects = [objects]
        self.attach_objects(objects)
        self.rescale_using_oxygen = tk.BooleanVar(value=True)
        self.plotted_files = []

    def attach_objects(self, objects: List[Any]) -> None:
        for o in objects:
            self.attach(o)

    def attach(self, object: Any, key: Optional[Any] = None) -> None:
        match object:
            case PlotControls():
                self._plot_controls = object
            case FileInfoPane():
                self._file_info_pane = object
            case FileList():
                match key:
                    case FileListType.PLOTTED:
                        self._plotted_file_list = object
                    case _:
                        self._file_list = object
            case FileListControls():
                self._file_list_controls = object
            case Plot():
                self._plot = object
            case FileInfoPane():
                self._file_info_pane = object
            case _:
                raise RuntimeError(f"Coordinator passed bad object {object}")

    def _configure_objects(self) -> None:
        self._file_list.file_listbox.bind("<<ListboxSelect>>", self.set_file_to_plot)
        self._file_list_controls.btRefresh.config(command=self.refresh_file_list)
        self._file_list_controls.btChangeDirectory.config(command=self.choose_directory)
        self._plot_controls.btClearPlot.config(command=self.clear_plot)
        self._plot_controls.btRemoveFromPlot.config(command=self.remove_from_plot)
        self._plot_controls.btViewCSD.config(command=self.plot_file)
        self._plot_controls.btAutoScale.config(command=self._plot.autoscale)
        self._plot_controls.set_button_status(True)

    def initialize(self) -> None:
        self._configure_objects()
        self.refresh_file_list()

    def choose_directory(self, *_):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self._file_list.current_directory = Path(new_directory)
            self._file_list.populate_listbox()
            self._file_list.update_label()

    def clear_plot(self, *_):
        self.plotted_files = []
        self.refresh_file_list()
        self._plot.clear_plot()
        self._plot_controls.set_button_status(False)
        clear_temp_files()

    def plot_file(self):
        file = self._file_list.get_selected_file()
        if file is not None:
            self.plotted_files.append(file)
            csd_file = download_filepair(file)
            file = CSDFile(csd_file, 1)
            self._plot.plot(file, self.rescale_using_oxygen.get())
            self._plotted_file_list.fill_list_box(self.plotted_files)
            self.refresh_file_list()

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
        files = [
            f
            for f in list(reversed(sorted(list_files())))
            if f not in self.plotted_files
        ]
        self._file_list.fill_list_box(files)
        self._plotted_file_list.fill_list_box(self.plotted_files)

    def set_file_to_plot(self, *_):
        file = self._file_list.get_selected_file()
        self._plot_controls.set_button_status(False)
