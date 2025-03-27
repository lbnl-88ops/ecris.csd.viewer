import tkinter as tk
import os
from tkinter import DISABLED, LEFT, NORMAL, RIGHT, filedialog
from pathlib import Path

class FileList(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.current_directory = os.getcwd()
        # Listbox to display files
        self.directory_label = tk.Label(self)
        self.update_label()
        self.directory_label.pack()

        self.file_listbox = tk.Listbox(self, width=50)
        self.file_listbox.pack()

        self.change_directory = tk.Button(self, text="Choose directory", 
                                     command=self.choose_directory)
        self.change_directory.pack(side=LEFT)
        self.refresh = tk.Button(self, text="Refresh", command=self.populate_listbox)
        self.refresh.pack(side=RIGHT)

        # Initial population (optional, current directory by default)
        self.populate_listbox()
    
    def update_label(self):
        self.directory_label.config(text=f"Current directory: {self.current_directory}")

    def populate_listbox(self):
        """Populates the listbox with files from the specified directory."""
        try:
            files = sorted(Path(self.current_directory).glob("csd_*"))
            self.file_listbox.delete(0, tk.END)  # Clear previous items
            if not files:
                self.file_listbox.insert(tk.END, 'No files found')
                self.file_listbox.configure(state=DISABLED)
            for file in files:
                self.file_listbox.insert(tk.END, file.name)
                self.file_listbox.configure(state=NORMAL)
        except FileNotFoundError:
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, "Directory not found.")
        except NotADirectoryError:
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, "Not a directory.")

    def choose_directory(self):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self.current_directory = new_directory
            self.populate_listbox()
            self.update_label()

# Create the main window
window = tk.Tk()
window.title("CSD Viewer")

# Directory input
# directory_label = tk.Label(window, text="Directory:")
# directory_label.pack()
# directory_entry = tk.Entry(window, width=50)
# directory_entry.pack()

# Change directory button
# change_button = tk.Button(window, text="Change Directory", command=change_directory)
# change_button.pack()

file_list = FileList(window)
file_list.pack()

window.mainloop()