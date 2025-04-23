import logging
import datetime as dt
import os
from pathlib import Path
from typing import List

from ecris.csd.viewer.analysis import CSD
from ecris.csd.viewer.analysis.io.read_csd_file import read_csd_from_file_pair

class CSDFile:
    def __init__(self, path, file_size: float = 0):
        self.path = path
        self.plotted: bool = False
        self.file_size: float = file_size
        self.valid: bool = True
        self.csd = None
        try:
            self.csd = read_csd_from_file_pair(path)
        except BaseException as e:
            logging.info(f'Failed to open {path}: {e}')
            self.valid = False


    @property
    def formatted_datetime(self) -> str:
        if self.csd:
            return self.csd.timestamp
        else:
            return 'File invalid'

    @property
    def list_value(self) -> str:
        return f"{self.formatted_datetime} ({self.path.name})"

def get_files(path: Path) -> List[CSDFile]:
    glob = "csd_" + "[0-9]"*10
    return [CSDFile(p, file_size=os.path.getsize(p)) 
            for p in reversed(sorted(Path(path).glob(glob)))]
