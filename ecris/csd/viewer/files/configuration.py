from dataclasses import dataclass, field
from logging import info
from pathlib import Path
from tomllib import load
from tkinter import messagebox
import tomllib
from typing import List

from appdirs import user_config_dir

from ecris.csd.analysis import Element

APP_NAME = 'csd_viewer'
APP_AUTHOR = 'lbnl_88ops'
CONFIG_FILENAME = 'config.toml'
CONFIG_FILEPATH = Path(user_config_dir(APP_NAME, APP_AUTHOR)) 
CONFIG_FULLPATH = CONFIG_FILEPATH / CONFIG_FILENAME

DATA_DIRECTORY = 'default_data_directory'

@dataclass
class AppConfiguration:
    default_directory: Path = Path('.')
    custom_elements: List[Element] = field(default_factory=list)

def load_configuration() -> AppConfiguration | None:
    if not CONFIG_FULLPATH.exists():
        return None
    else:
        try:
            with open(CONFIG_FULLPATH, 'rb') as f:
                config = load(f)
                custom_elements = []
                if 'element' in config:
                    info('Custom elements found')
                    for name, data in config['element'].items():
                        info(f'Parsing custom element: {name}')
                        try:
                            custom_elements.append(
                                Element(name=name, symbol=data['symbol'],
                                        atomic_weight=data['atomic_mass'], 
                                        atomic_number=data['atomic_number']))
                            info(f'Parsed element {custom_elements[-1]}')
                        except KeyError as e:
                            info(f'Error parsing custom element: {e}')
                            continue
                return AppConfiguration(
                    default_directory=Path(config[DATA_DIRECTORY]).absolute(),
                    custom_elements=custom_elements,
                )
        except tomllib.TOMLDecodeError:
            messagebox.showerror('Error', 
                                 'Error loading configuration, using default settings')
            return AppConfiguration()

def create_configuration() -> AppConfiguration:
    CONFIG_FILEPATH.mkdir(exist_ok=True)
    with open(CONFIG_FULLPATH, 'w') as f:
        f.write(f'{DATA_DIRECTORY} = "."')
        f.write('\n\n')
        f.write('\n'.join(["# Add custom elements like so:", 
                           '# [element."Uranium"]', 
                           '# symbol="U"', 
                           '# atomic_mass=235', 
                           '# atomic_number=92']))

    config = load_configuration()
    if config is None:
        raise RuntimeError
    return config