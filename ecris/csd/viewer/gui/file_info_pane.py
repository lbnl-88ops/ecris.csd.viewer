import tkinter as tk
import ttkbootstrap as ttk

from ecris.csd.viewer.files import CSDFile

class FileInfoPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._font = "TkDefaultFont"
        self._title_font = (self._font, 14)
        self._subtitle_font = (self._font, 12)
        self._info_widgets = []
        self._info = {}
        self.visible = False

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text='File Info', font=self._title_font).pack()
        self._info_frame = ttk.Frame(self)
        self._info_frame.columnconfigure(0, weight=1)
        self._info_frame.columnconfigure(1, weight=10)
        for i, (name, attribute) in enumerate(zip(['Filename', 'Time Stamp'], 
                                                  ['filename', 'timestamp'])):
            self._info[attribute] = tk.StringVar(value='No file selected')
            ttk.Label(self._info_frame, text=name, 
                      justify='left').grid(column=0, row=i, sticky='w')
            ttk.Label(self._info_frame, textvariable=self._info[attribute], 
                      justify='right').grid(column=1, row=i, sticky='e')
        self._info_frame.pack()

    def clear_frames(self):
        for frame in [self._info_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

    def update_info(self, file: CSDFile | None = None):
        if file is None:
            for attribute, variable in self._info.items():
                variable.set('No file selected')
        else:
            for attribute, variable in self._info.items():
                variable.set(str(getattr(file, attribute)))