from pathlib import Path
import tkinter as tk
from typing import List
import ttkbootstrap as ttk

from csd_viewer.files import CSDFile, get_files
from csd_viewer.gui.info_frame import FileInfoPane

BLUE = "#5200FF"
WHITE = "#FFFFFF"


class FileList(tk.Frame):
    def __init__(self, owner, path: Path, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self.owner = owner
        self.current_directory = path

        # Listbox to display files
        self.directory_label = tk.Label(self)
        self.update_label()
        self.directory_label.pack(side="top")

        self.files: List[CSDFile] = []
        self.stringvar = tk.Variable(value=["No CSD files found"])
        self.file_listbox = tk.Listbox(
            self, width=50, selectmode=tk.SINGLE, listvariable=self.stringvar
        )
        self.file_listbox.pack(side="left", fill="y")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical")
        self.scrollbar.config(command=self.file_listbox.yview)
        self.scrollbar.pack(side="left", fill="y")
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        self.populate_listbox()

    def update_label(self):
        self.directory_label.config(text=f"Viewing: {self.current_directory}")

    def get_selected_file(self) -> CSDFile | None:
        for i in self.file_listbox.curselection():
            return self.files[i]

    def clear_loaded(self) -> None:
        for file in [f for f in self.files if not f.plotted]:
            file.unload_csd()

    def update_colors(self):
        colors = ttk.Style().colors
        for i, file in enumerate(self.files):
            if file.plotted and file.valid:
                self.file_listbox.itemconfigure(
                    i,
                    foreground=colors.success,
                    selectbackground=colors.success,
                    selectforeground="white",
                )
            elif not file.valid:
                self.file_listbox.itemconfigure(
                    i,
                    foreground="gray",
                    selectbackground="white",
                    selectforeground="gray",
                )
            else:
                self.file_listbox.itemconfigure(
                    i,
                    foreground=colors.fg,
                    selectbackground=colors.primary,
                    selectforeground="white",
                )

    def populate_listbox(self, retain_plotted=False):
        old_plotted_files = {}
        if retain_plotted:
            old_plotted_files = {f.path: f for f in self.files if f.plotted}

        current_files_on_disk = get_files(self.current_directory)

        new_file_list = []
        for file_obj in current_files_on_disk:
            if file_obj.path in old_plotted_files:
                new_file_list.append(old_plotted_files[file_obj.path])
            else:
                new_file_list.append(file_obj)

        self.files = new_file_list

        self.file_listbox.delete(0, tk.END)
        if not self.files:
            self.stringvar.set(["No CSD files found"])
            self.file_listbox.configure(state=tk.DISABLED)
        else:
            self.stringvar.set([f.list_value for f in self.files])
            self.file_listbox.configure(state=tk.NORMAL)

        self.update_colors()
