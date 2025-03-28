import tkinter as tk
import os
from tkinter import DISABLED, E, LEFT, N, NORMAL, RIGHT, SINGLE, W, S, filedialog
from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ecris.csd.viewer import get_plot

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSD Viewer")
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        self.destroy()

    def view_csd(self):
        self.plot.plot(self.file_list.get_selected_filename())

    def create_widgets(self):
        self.file_list = FileList(self)
        self.file_list.grid(row=0, column =1, padx=1, pady=1) 
        self.plot = Plot(self)
        self.plot.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        view_button = tk.Button(self, text="View CSD", command=self.view_csd)
        view_button.grid(row=1, column=1, padx = 10, pady=10, sticky=W)

class Plot(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.canvas = None

    def plot(self, file: Path):
        if self.canvas is not None:
            for widget in self.winfo_children():
                widget.destroy()
        self.canvas = FigureCanvasTkAgg(get_plot(file), master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()

class FileList(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.current_directory = os.getcwd()
        # Listbox to display files
        self.directory_label = tk.Label(self)
        self.update_label()
        self.directory_label.pack()

        self.file_listbox = tk.Listbox(self, width=50, selectmode=SINGLE)
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

    def get_selected_filename(self) -> Path:
        for i in self.file_listbox.curselection():
            return Path(self.current_directory) / self.file_listbox.get(i)

    def populate_listbox(self):
        """Populates the listbox with files from the specified directory."""
        try:
            files = reversed(sorted(Path(self.current_directory).glob("csd_*")))
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

app = App()
app.mainloop()
