import logging
import datetime as dt
from pathlib import Path

import numpy as np

from ecris.csd.viewer.analysis.model import CSD

DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

def file_timestamp(file: Path) -> str:
    try:
        return dt.datetime.fromtimestamp(float(file.name[-10:])).strftime(DATETIME_FORMAT)
    except BaseException as e:
        logging.info(f'Failed to parse timestamp for file {file}: {e}')
        return 'Invalid timestamp'

def read_csd_from_file_pair(csd_file: Path) -> CSD:
    data = np.loadtxt(csd_file)
    timestamp = file_timestamp(csd_file)
    settings = {}
    with open(csd_file.with_name(csd_file.name.replace('csd', 'dsht')),'r') as f:
        for setting in f.readlines():
            _, value, name = setting.split()
            settings[name] = float(value)
    return CSD(data=data, timestamp=timestamp, settings=settings)
