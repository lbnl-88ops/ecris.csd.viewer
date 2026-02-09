from pathlib import Path

import yaml

from csd_viewer import CSDViewer
from csd_viewer.files.configuration import load_configuration, AppConfiguration


def csd_viewer():
    app = CSDViewer(load_configuration())
    app.mainloop()


# Create the main window
if __name__ == "__main__":
    csd_viewer()
