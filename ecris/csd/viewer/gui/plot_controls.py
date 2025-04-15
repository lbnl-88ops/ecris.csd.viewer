import tkinter as tk

from .file_list import FileList
from .plot import Plot

class PlotControls(tk.Frame):
    def __init__(self, plot: Plot, file_list: FileList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pad = 3.0
        self.big_button_size = 2
        self.file_list = file_list
        self.plot = plot
        self.create_widgets()
    
    def create_widgets(self):
        self.widgets = []
        self.btChangeDirectory = tk.Button(self, text="Choose directory", 
                                     command=self.choose_directory)
        self.btRefresh = tk.Button(self, text="Refresh", 
                                 command=self.refresh)
        self.btViewCSD = tk.Button(self, text="Plot CSD",
                                  command=self.plot_file,
                                  height=self.big_button_size)
        self.btClearPlot = tk.Button(self, text="Clear Plot", 
                                     command=self.clear_plot, 
                                     height=self.big_button_size)
        for loc, widget in {
            (0, 0): self.btViewCSD, 
            (0, 1): self.btClearPlot,
            (1, 0): self.btChangeDirectory, 
            (1, 1): self.btRefresh, 
            }.items():
            widget.grid(row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky='nsew')

    def plot_file(self):
        file = self.file_list.get_selected_file()
        if file is not None:
            self.plot.plot(file)
            file.plotted = True
            self.file_list.update_colors()

    def clear_plot(self):
        for i, file in enumerate(self.plot._plotted_files):
            self.plot._plotted_files[i].plotted = False
        self.plot._plotted_files = []
        self.plot.clear_plot()
        self.file_list.populate_listbox()

    def choose_directory(self):
        new_directory = tk.filedialog.askdirectory()
        if new_directory:
            self.file_list.current_directory = new_directory
            self.file_list.populate_listbox()
            self.file_list.update_label()

    def refresh(self):
        self.file_list.populate_listbox(retain_plotted=True)