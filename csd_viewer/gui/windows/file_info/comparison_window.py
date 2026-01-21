import tkinter as tk


class FileComparisonWindow(tk.Toplevel):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, takefocus=True)
        self.title("CSD File Comparison -- CSD Viewer")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.destroy()
