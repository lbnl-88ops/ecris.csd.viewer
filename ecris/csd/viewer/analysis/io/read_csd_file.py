import datetime as dt
from pathlib import Path

import numpy as np

from ecris.csd.viewer.analysis.model import CSD

DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

def read_csd_from_file_pair(csd_file: Path) -> CSD:
    data = np.loadtxt(csd_file)
    timestamp = dt.datetime.fromtimestamp(float(csd_file.name[-10:])).strftime(DATETIME_FORMAT)
    settings = {}
    with open(csd_file.with_name(csd_file.name.replace('csd', 'dsht')),'r') as f:
        for setting in f.readlines():
            _, value, name = setting.split()
            settings[name] = float(value)
    return CSD(data=data, timestamp=timestamp, settings=settings)
