import logging
import datetime as dt
import os
from pathlib import Path
from typing import List

from ecris.csd.analysis import CSD
from ecris.csd.analysis.io.read_csd_file import read_csd_from_file_pair, file_timestamp

class CSDFile:
    def __init__(self, path, file_size: float = 0):
        self.path = path
        self.plotted: bool = False
        self.file_size: float = file_size
        self.valid: bool = True
        self.timestamp = file_timestamp(path)
        self._csd = None

    @property
    def formatted_datetime(self) -> str:
        return self.timestamp

    def unload_csd(self) -> None:
        self._csd = None

    @property
    def csd(self) -> CSD | None:
        try:
            if self._csd is None:
                self.valid = True
                return read_csd_from_file_pair(self.path)
            else:
                return self._csd
        except BaseException as e:
            logging.info(f'File is invalid: {self.path}: {e}')
            self.valid = False
            return None

    @property
    def list_value(self) -> str:
        return f"{self.formatted_datetime} ({self.path.name})"

def get_files(path: Path) -> List[CSDFile]:
    glob = "csd_" + "[0-9]"*10
    return [CSDFile(p, file_size=os.path.getsize(p)) 
            for p in reversed(sorted(Path(path).glob(glob)))]
