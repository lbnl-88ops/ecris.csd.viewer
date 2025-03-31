import datetime as dt
import os
from pathlib import Path
from typing import List

class CSDFile():
    def __init__(self, path, file_size: float = 0):
        self.path = path
        self.datetime_format: str = "%Y-%m-%d %H:%M:%S"
        self.plotted: bool = False
        self.file_size: float = file_size

    @property
    def formatted_datetime(self) -> str:
        time_stamp = self.path.name[-10:]
        print(time_stamp)
        return dt.datetime.fromtimestamp(float(time_stamp)).strftime(self.datetime_format)

    @property
    def list_value(self) -> str:
        return f"{self.formatted_datetime} ({self.path.name})"

def get_files(path: Path) -> List[CSDFile]:
        return [CSDFile(p, 
                        file_size=os.path.getsize(p)) 
                        for p in reversed(sorted(Path(path).glob("csd_*")))]
