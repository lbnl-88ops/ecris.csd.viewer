from pathlib import Path
from tkinter import filedialog
from typing import Any, List

from ecris.csd.viewer.gui.controls.controls import FileListControls, PlotControls
from ecris.csd.viewer.gui.controls.file_list import FileList
from ecris.csd.viewer.gui.info_frame.file_info_pane import FileInfoPane


class Coordinator:
    def __init__(self, objects: Any | List[Any]):
        if not isinstance(objects, List):
            objects = [objects]
        self.attach(objects)
        self.configure_objects()
        

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
                case _:
                    raise RuntimeError(f'Coordinator passed bad object {object}')
    
    def configure_objects(self) -> None:
        self._file_list.file_listbox.bind("<<ListboxSelect>>", self.set_selected_file)
        self._file_list_controls.btRefresh.config(command=self.refresh_file_list)
        self._file_list_controls.btChangeDirectory.config(command=self.choose_directory)

    def choose_directory(self, *_):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self._file_list.current_directory = Path(new_directory)
            self._file_list.populate_listbox()
            self._file_list.update_label()

    def refresh_file_list(self, *_):
        self._file_list.populate_listbox(retain_plotted=True)

    def set_selected_file(self, *_):
        file = self._file_list.get_selected_file()
        self._file_info_pane.update_info(file)
        if file is not None:
            self._plot_controls.set_button_status(file.plotted)
