import tkinter as tk

from .files.file_list import FileList
from .plotting.plot import Plot

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
        self.change_directory.grid(row=0, column=0, padx=self.pad, pady=self.pad,
                                   sticky='nsew')
        self.refresh = tk.Button(self, text="Refresh", 
                                 command=self.refresh)
        self.refresh.grid(row=0, column=1, padx=self.pad, pady=self.pad,
                          sticky='nsew')
        self.view_csd = tk.Button(self, text="Plot CSD",
                                  command=self.plot_file)
        self.view_csd.grid(row=1, column=0, padx=self.pad, pady=self.pad,
                           sticky='nsew')
        self.clear_plot = tk.Button(self, text="Clear Plot",
                                    command=self.clear_plot)
        self.clear_plot.grid(row=1, column=1, padx=self.pad, pady=self.pad,
                             sticky='nsew')

    def plot_file(self):
        file = self.file_list.get_selected_file()
        if file is not None:
            self.plot.plot(file)
            file.plotted = True
            self.file_list.update_colors()

    def clear_plot(self):
        for i, file in enumerate(self.plot.plotted_files):
            self.plot.plotted_files[i].plotted = False
        self.plot.plotted_files = []
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