from dataclasses import dataclass
from pathlib import Path
from tomllib import load
from tkinter import messagebox
import tomllib

from appdirs import user_config_dir

APP_NAME = 'csd_viewer'
APP_AUTHOR = 'lbnl_88ops'
CONFIG_FILENAME = 'config.toml'
CONFIG_FILEPATH = Path(user_config_dir(APP_NAME, APP_AUTHOR)) 
CONFIG_FULLPATH = CONFIG_FILEPATH / CONFIG_FILENAME

DATA_DIRECTORY = 'default_data_directory'

@dataclass
class AppConfiguration:
    default_directory: Path = Path('.')

def load_configuration() -> AppConfiguration | None:
    if not CONFIG_FULLPATH.exists():
        return None
    else:
        try:
            with open(CONFIG_FULLPATH, 'rb') as f:
                config = load(f)
                return AppConfiguration(
                    default_directory=Path(config[DATA_DIRECTORY]).absolute(),
                )
        except tomllib.TOMLDecodeError:
            messagebox.showerror('Error', 
                                 'Error loading configuration, using default settings')
            return AppConfiguration()

def create_configuration() -> AppConfiguration:
    CONFIG_FILEPATH.mkdir(exist_ok=True)
    with open(CONFIG_FULLPATH, 'w') as f:
        f.write(f'{DATA_DIRECTORY} = "."')
    config = load_configuration()
    if config is None:
        raise RuntimeError
    return config