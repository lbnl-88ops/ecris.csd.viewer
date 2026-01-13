from logging import getLogger
from pathlib import Path
import tempfile
from typing import List

import requests

_log = getLogger(__name__)

API_URL = "http://ecris.lbl.gov:5000"


def list_files() -> List[Path]:
    url = f"{API_URL}/files"
    response = requests.get(url)
    if response.status_code == 200:
        return [Path(filename) for filename in response.json()]
    else:
        _log.error(f"Failed to retrieve files from {url}")
        return []


def download_filepair(filepath: Path):
    csd_filename = str(filepath.name)
    dsht_filename = csd_filename.replace("csd", "dsht")
    download_file(dsht_filename)
    return download_file(csd_filename)


def download_file(filename: str) -> Path | None:
    """Download a file from the API and save it as a temporary file."""
    _log.info(f"Attempting to download {filename}")
    temp_folder = Path("./tmp/")
    temp_folder.mkdir(exist_ok=True)
    response = requests.get(f"{API_URL}/download/{filename}")
    if response.status_code == 200:
        temp_file = temp_folder / filename
        with open(temp_file, "wb") as f:
            f.write(response.content)
        return temp_file
    else:
        print("File not found on server.")
        return None
