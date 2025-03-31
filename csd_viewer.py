from pathlib import Path

import yaml

from ecris.csd.viewer import CSDViewer

def csd_viewer():
    try:
        with open('config.yaml') as f:
            configuration = yaml.load(f, Loader=yaml.Loader)
        print(configuration)
        default_path = Path(configuration['default_directory'])
    except Exception as exc:
        print(exc)
        default_path = Path('.')

    app = CSDViewer(default_path)
    app.mainloop()

# Create the main window
if __name__ == '__main__':
    csd_viewer()
