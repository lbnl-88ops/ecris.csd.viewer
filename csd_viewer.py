from ecris.csd.viewer import CSDViewer

def csd_viewer():
    app = CSDViewer()
    app.mainloop()

# Create the main window
if __name__ == '__main__':
    csd_viewer()
