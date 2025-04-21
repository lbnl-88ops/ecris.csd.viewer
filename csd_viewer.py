from pathlib import Path

import yaml

from ecris.csd.viewer import CSDViewer
from ecris.csd.viewer.files.configuration import load_configuration, AppConfiguration

def csd_viewer():

    app = CSDViewer(load_configuration())
    app.mainloop()

# Create the main window
if __name__ == '__main__':
    csd_viewer()
