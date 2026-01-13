from enum import Enum, auto
from logging import getLogger
from pathlib import Path
from tkinter import filedialog
from typing import Any, List, Optional
import tkinter as tk
import time
from datetime import datetime

from csd_viewer.files.csd_file import CSDFile
from csd_viewer.gui.controls.controls import FileListControls, PlotControls
from csd_viewer.gui.controls.file_list import FileList
from csd_viewer.gui.info_frame.file_info_pane import FileInfoPane
from csd_viewer.gui import Plot, FileInfoPane
from csd_viewer.files.client import (
    list_files,
    download_filepair,
    clear_temp_files,
    API_URL,
)

_log = getLogger(__name__)


# TODO: roll this into WidgetType
class FileListType(Enum):
    TO_PLOT = auto()
    PLOTTED = auto()


class FileMode(Enum):
    LOCAL = auto()
    REMOTE = auto()


class WidgetType(Enum):
    STATUS_STRING = auto()


class Coordinator:
    def __init__(self, objects: Any | List[Any]):
        if not isinstance(objects, List):
            objects = [objects]
        self.attach_objects(objects)
        self.rescale_using_oxygen = tk.BooleanVar(value=True)
        self.plotted_files = []
        self.mode = FileMode.REMOTE
        self._last_updated = "N/A"
        self._files_available = 0

    def attach_objects(self, objects: List[Any]) -> None:
        for o in objects:
            self.attach(o)

    def attach(self, object: Any, key: Optional[Any] = None) -> None:
        if key is not None:
            match key:
                case WidgetType.STATUS_STRING:
                    self._status_string = object
                    return
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
        self._file_list.file_listbox.bind(
            "<<ListboxSelect>>", self.update_button_states
        )
        self._plotted_file_list.file_listbox.bind(
            "<<ListboxSelect>>", self.update_button_states
        )
        self._file_list_controls.btRefresh.config(command=self.refresh_file_list)
        self._file_list_controls.btChangeDirectory.config(command=self.choose_directory)
        self._plot_controls.btClearPlot.config(command=self.clear_plot)
        self._plot_controls.btRemoveFromPlot.config(command=self.remove_from_plot)
        self._plot_controls.btPlotCSD.config(command=self.plot_file)
        self._plot_controls.btAutoScale.config(command=self._plot.autoscale)
        # self._plot_controls.set_button_status(True)

    def update_button_states(self, *_):
        if self._file_list.file_listbox.curselection():
            self._plot_controls.activate_buttons(True, False)  # Can plot
        elif self._plotted_file_list.file_listbox.curselection():
            self._plot_controls.activate_buttons(False, True)  # Can remove
        else:
            self._plot_controls.activate_buttons(False, False)

    def update_status(self) -> None:
        if self.mode == FileMode.REMOTE:
            self._status_string.set(
                f"Connected to {API_URL}\nLast update {self._last_updated}, {self._files_available} files found"
            )

    def initialize(self) -> None:
        self._configure_objects()
        self.update_status()
        self.refresh_file_list()

    def choose_directory(self, *_):
        new_directory = filedialog.askdirectory()
        pass

    def clear_plot(self, *_):
        self.plotted_files = []
        self.refresh_file_list()
        self._plot.clear_plot()
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
        current_time = time.time()
        dt_object = datetime.fromtimestamp(current_time)
        self._last_updated = dt_object.strftime("%Y-%m-%d %H:%M")
        match self.mode:
            case FileMode.REMOTE:
                found_files = list(reversed(sorted(list_files())))
                self._files_available = len(found_files)
        files = [f for f in found_files if f not in self.plotted_files]
        self._file_list.fill_list_box(files)
        self._plotted_file_list.fill_list_box(self.plotted_files)
        self.update_status()
        self.update_button_states()
