from typing import Any, List

from ecris.csd.viewer.files.csd_file import CSDFile
from ecris.csd.viewer.gui.controls.controls import PlotControls
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
                case _:
                    raise RuntimeError(f'Coordinator passed bad object {object}')
    
    def configure_objects(self) -> None:
        self._file_list.file_listbox.bind("<<ListboxSelect>>", self.set_selected_file)


    def set_selected_file(self, *_):
        file = self._file_list.get_selected_file()
        self._file_info_pane.update_info(file)
        self._plot_controls.set_button_status(file.plotted)
