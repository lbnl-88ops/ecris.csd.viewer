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
        self.pad = 1.0
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        self.destroy()

    def create_widgets(self):
        self.file_list = FileList()
        self.file_list.grid(row=0, column =1, padx=self.pad, pady=self.pad, sticky="nsew") 
        self.plot = Plot(self)
        self.plot.grid(row=0, column=0, padx=self.pad, pady=self.pad, sticky="nsew")
        self.controls = PlotControls(self.plot, self.file_list)
        self.controls.grid(row=1, column=1, padx=self.pad, pady=self.pad, sticky="n")


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



class PlotControls(tk.Frame):
    def __init__(self, plot: Plot, file_list: FileList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pad = 3.0
        self.file_list = file_list
        self.plot = plot
        self.create_widgets()
    
    def create_widgets(self):
        self.change_directory = tk.Button(self, text="Choose directory", 
                                     command=self.choose_directory)
        self.refresh = tk.Button(self, text="Refresh", 
                                 command=self.refresh)
        self.change_directory.grid(row=0, column=0, padx=self.pad, pady=self.pad)
        self.refresh.grid(row=0, column=1, padx=self.pad, pady=self.pad)

    def choose_directory(self):
        new_directory = filedialog.askdirectory()
        if new_directory:
            self.file_list.current_directory = new_directory
            self.file_list.populate_listbox()
            self.file_list.update_label()

    def refresh(self):
        self.file_list.populate_listbox()

# Create the main window

app = App()
app.mainloop()
