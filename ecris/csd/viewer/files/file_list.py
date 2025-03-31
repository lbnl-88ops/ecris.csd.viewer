from pathlib import Path
import os
import tkinter as tk


class FileList(tk.Frame):
    def __init__(self, path: Path, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.current_directory = path

        # Listbox to display files
        self.directory_label = tk.Label(self)
        self.update_label()
        self.directory_label.pack()

        self.file_listbox = tk.Listbox(self, width=50, selectmode=tk.SINGLE)
        self.file_listbox.pack()

        self.populate_listbox()
    
    def update_label(self):
        self.directory_label.config(text=f"Current directory: {self.current_directory}")

    def get_selected_filename(self) -> Path:
        for i in self.file_listbox.curselection():
            return Path(self.current_directory) / self.file_listbox.get(i)
    
    def get_most_recent_filename(self) -> Path:
        return Path(self.current_directory) / self.file_listbox.get(0)

    def populate_listbox(self):
        """Populates the listbox with files from the specified directory."""
        try:
            files = reversed(sorted(Path(self.current_directory).glob("csd_*")))
            self.file_listbox.delete(0, tk.END)  # Clear previous items
            if not files:
                self.file_listbox.insert(tk.END, 'No files found')
                self.file_listbox.configure(state=tk.DISABLED)
            for file in files:
                self.file_listbox.insert(tk.END, file.name)
                self.file_listbox.configure(state=tk.NORMAL)
        except FileNotFoundError:
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, "Directory not found.")
        except NotADirectoryError:
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, "Not a directory.")