from pathlib import Path
import tkinter as tk
from typing import List
import ttkbootstrap as ttk

from ..files.csd_file import CSDFile, get_files

BLUE = "#5200FF"
WHITE = "#FFFFFF"

class FileList(tk.Frame):
    def __init__(self, owner, path: Path, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self.current_directory = path

        # Listbox to display files
        self.directory_label = tk.Label(self)
        self.update_label()
        self.directory_label.pack(side='top')

        self.files: List[CSDFile] = []
        self.stringvar = tk.StringVar(value=["No CSD files found"])
        self.file_listbox = tk.Listbox(self, width=50, selectmode=tk.SINGLE,
                                       listvariable=self.stringvar)
        self.file_listbox.pack(side='left', fill='y')
        self.scrollbar = tk.Scrollbar(self, orient='vertical', width=20)
        self.scrollbar.config(command=self.file_listbox.yview)
        self.scrollbar.pack(side='left', fill='y')
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        self.populate_listbox()
    
    def update_label(self):
        self.directory_label.config(text=f"Viewing: {self.current_directory}")
    
    def get_selected_file(self) -> CSDFile:
        for i in self.file_listbox.curselection():
            return self.files[i]

    def update_colors(self):
        style = ttk.Style()
        for i, file in enumerate(self.files):
            if file.plotted and file.valid:
                self.file_listbox.itemconfigure(i, 
                                                foreground=style.colors.success,
                                                selectbackground=style.colors.success,
                                                selectforeground='white')
            elif not file.valid:
                self.file_listbox.itemconfigure(i, foreground="gray",
                                                selectbackground='white',
                                                selectforeground='gray')
            else:
                self.file_listbox.itemconfigure(i, foreground=style.colors.fg,
                                                selectbackground=style.colors.primary,
                                                selectforeground='white')

    def populate_listbox(self, retain_plotted=False):
        """Populates the listbox with files from the specified directory."""
        plotted = []
        if retain_plotted:
            plotted = [f.path for f in self.files if f.plotted]
        self.files = get_files(self.current_directory)
        self.file_listbox.delete(0, tk.END)
        if not self.files:
            self.stringvar.set(["No CSD files found"])
            self.file_listbox.configure(state=tk.DISABLED)
        else:
            self.stringvar.set([f.list_value for f in self.files])
            self.file_listbox.configure(state=tk.NORMAL)
        for file in self.files:
            file.plotted = file.path in plotted
        self.update_colors()
        
