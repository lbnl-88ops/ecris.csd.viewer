from logging import getLogger
from pathlib import Path
from typing import List

import requests

_log = getLogger(__name__)

API_URL = "http://127.0.0.1:5000"


def list_files() -> List[Path]:
    url = f"{API_URL}/files"
    response = requests.get(url)
    if response.status_code == 200:
        return [Path(filename) for filename in response.json()]
    else:
        _log.error(f"Failed to retrieve files from {url}")
        return []
