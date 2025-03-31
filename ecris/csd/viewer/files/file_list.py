from pathlib import Path
import tkinter as tk
from typing import List

from .csd_file import CSDFile, get_files

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
    
    def get_selected_file(self) -> CSDFile:
        for i in self.file_listbox.curselection():
            return self.files[i]

    def update_colors(self):
        for i, file in enumerate(self.files):
            if file.plotted:
                self.file_listbox.itemconfigure(i, foreground="#555555") 

    def populate_listbox(self):
        """Populates the listbox with files from the specified directory."""
        self.files = get_files(self.current_directory)
        self.file_listbox.delete(0, tk.END)
        if not self.files:
            self.stringvar.set(["No CSD files found"])
            self.file_listbox.configure(state=tk.DISABLED)
        else:
            self.stringvar.set([f.list_value for f in self.files])
            self.file_listbox.configure(state=tk.NORMAL)
        self.update_colors()
