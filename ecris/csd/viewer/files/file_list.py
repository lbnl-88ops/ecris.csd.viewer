import datetime as dt
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from typing import List

class CSDFile():
    def __init__(self, path):
        self.path = path
        self.datetime_format: str = "%Y-%m-%d %H:%M:%S"
        self.plotted: bool = False
        self.file_size: float = 0

    @property
    def formatted_datetime(self) -> str:
        time_stamp = self.path.name[-10:]
        print(time_stamp)
        return dt.datetime.fromtimestamp(float(time_stamp)).strftime(self.datetime_format)

    @property
    def list_value(self) -> str:
        return f"{self.formatted_datetime} ({self.path.name})"

class FileList(tk.Frame):
    def __init__(self, path: Path, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.current_directory = path

        # Listbox to display files
        self.directory_label = tk.Label(self)
        self.update_label()
        self.directory_label.pack()

        self.files: List[CSDFile] = []
        self.stringvar = tk.StringVar(value=["No CSD files found"])
        self.file_listbox = tk.Listbox(self, width=50, selectmode=tk.SINGLE,
                                       listvariable=self.stringvar)
        self.file_listbox.pack()
        self.populate_listbox()
    
    def update_label(self):
        self.directory_label.config(text=f"Current directory: {self.current_directory}")
    
    def get_files(self):
        self.files = [CSDFile(p) for p in reversed(
            sorted(Path(self.current_directory).glob("csd_*")))]

    def get_selected_filename(self) -> Path:
        for i in self.file_listbox.curselection():
            return Path(self.current_directory) / self.file_listbox.get(i)
    
    def get_most_recent_filename(self) -> Path:
        return Path(self.current_directory) / self.file_listbox.get(0)

    def populate_listbox(self):
        """Populates the listbox with files from the specified directory."""
        self.get_files()
        self.file_listbox.delete(0, tk.END)
        if not self.files:
            self.stringvar.set(["No CSD files found"])
            self.file_listbox.configure(state=tk.DISABLED)
        else:
            self.stringvar.set([f.list_value for f in self.files])
            self.file_listbox.configure(state=tk.NORMAL)
