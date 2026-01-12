import tkinter as tk

import ttkbootstrap as ttk


class FileListControls(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.pad = 3.0
        self.create_widgets()

    def create_widgets(self):
        self.btChangeDirectory = ttk.Button(
            self, text="Choose directory", bootstyle="primary"
        )
        self.btRefresh = ttk.Button(
            self, text="Refresh file list", bootstyle="primary-outline"
        )
        for loc, widget in {
            (0, 0): self.btChangeDirectory,
            (0, 1): self.btRefresh,
        }.items():
            widget.grid(
                row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky="nsew"
            )


class PlotControls(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.pad = 3.0
        self.big_button_size = 2
        self.create_widgets()

    def create_widgets(self):
        self.widgets = []
        self.btViewCSD = ttk.Button(self, text="Plot CSD", bootstyle="success")
        self.btAutoScale = ttk.Button(
            self, text="Reset Scale", bootstyle="success-outline"
        )
        self.btRemoveFromPlot = ttk.Button(
            self, text="Remove from plot", state="disabled", bootstyle="outline+danger"
        )
        self.btClearPlot = ttk.Button(self, text="Clear Plot", bootstyle="outline")
        for loc, widget in {
            (0, 0): self.btViewCSD,
            (0, 1): self.btAutoScale,
            (0, 2): self.btRemoveFromPlot,
            (0, 3): self.btClearPlot,
        }.items():
            widget.grid(
                row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky="nsew"
            )

    def set_button_status(self, file_is_plotted=False):
        if file_is_plotted:
            self.btViewCSD.config(state="disabled")
            self.btRemoveFromPlot.config(state="enabled")
        else:
            self.btViewCSD.config(state="enabled")
            self.btRemoveFromPlot.config(state="disabled")
