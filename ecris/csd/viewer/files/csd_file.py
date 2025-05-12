import logging
import datetime as dt
import os
from pathlib import Path
from typing import List

from matplotlib.artist import Artist

from ecris.csd.analysis import CSD
from ecris.csd.analysis.io.read_csd_file import read_csd_from_file_pair, file_timestamp

class CSDFile:
    def __init__(self, path, file_size: float = 0):
        self.path = path
        self.filename = self.path.name
        self.plotted: bool = False
        self.file_size: float = file_size
        self.valid: bool = True
        self.timestamp = file_timestamp(path)
        self._csd = None
        self._artist = None

    @property
    def artist(self) -> Artist | None:
        return self._artist

    @artist.setter
    def artist(self, to_set):
        self._artist = to_set 
    
    def clear_artist(self):
        if self._artist is not None:
            self._artist.remove()
            self._artist = None

    @property
    def formatted_datetime(self) -> str:
        return self.timestamp

    def unload_csd(self) -> None:
        self._csd = None

    @property
    def csd(self) -> CSD | None:
        if not self.valid:
            return None
        try:
            if self._csd is None:
                self.valid = True
                self._csd = read_csd_from_file_pair(self.path)
            return self._csd
        except BaseException as e:
            logging.info(f'File is invalid: {self.path}: {e}')
            self.valid = False
            return None

    @property
    def list_value(self) -> str:
        return f"{self.formatted_datetime}"

def get_files(path: Path) -> List[CSDFile]:
    glob = "csd_" + "[0-9]"*10
    return [CSDFile(p, file_size=os.path.getsize(p)) 
            for p in reversed(sorted(Path(path).glob(glob)))]
