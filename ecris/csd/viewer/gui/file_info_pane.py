import tkinter as tk
import ttkbootstrap as ttk

class FileInfoPane(ttk.Frame):
    def init(self, owner, *args, **kwargs):
        super().__init__(owner, width=100, *args, **kwargs)
        tk.Label(self, text='File Information')