import tkinter as tk
import ttkbootstrap as ttk

from ecris.csd.analysis import CSD
from ecris.csd.viewer.files import CSDFile

class CSDInfo:
    def __init__(self, csd: CSD):
        self._csd = csd
        self.data_points = len(csd.time)
        self.extraction_voltage = csd.extraction_voltage

class FileInfoPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._font = "TkDefaultFont"
        self._title_font = (self._font, 14)
        self._subtitle_font = (self._font, 12)
        self._info_widgets = []
        self._file_info = {}
        self._csd_info = {}
        self.visible = tk.BooleanVar(value=False)
        self.visible.trace_add('write', self.set_visible)

        self.create_widgets()

    def set_visible(self, *args, **kwargs):
        if not self.visible.get():
            self.pack_forget()
        else:
            self.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    def create_widgets(self):
        tk.Label(self, text='File Info', font=self._title_font).pack()
        self._info_frame = ttk.Frame(self)
        for i, (name, attribute) in enumerate(zip(['Filename', 'Time Stamp'], 
                                                  ['filename', 'timestamp'])):
            self._file_info[attribute] = tk.StringVar(value='No file selected')
            ttk.Label(self._info_frame, text=name, 
                      justify='left').grid(column=0, row=i, sticky='w')
            ttk.Label(self._info_frame, textvariable=self._file_info[attribute], 
                      justify='right').grid(column=1, row=i, sticky='e')
        self._info_frame.pack()
        tk.Label(self, text='CSD Info', font=self._title_font).pack()
        self._csd_info_frame = ttk.Frame(self)
        for i, (name, attribute) in enumerate(zip(['Data Points', 'Extraction Voltage'],
                                                  ['data_points', 'extraction_voltage'])):
            self._csd_info[attribute] = tk.StringVar(value='No file selected')
            ttk.Label(self._csd_info_frame, text=name,
                      justify='left').grid(column=0, row=i, sticky='w')
            ttk.Label(self._csd_info_frame, textvariable=self._csd_info[attribute], 
                      justify='right').grid(column=1, row=i, sticky='e')
        self._csd_info_frame.pack()

        self.btRemovePlot = ttk.Button(self,
                                       text="Remove from plot",
                                       bootstyle=(ttk.DANGER, ttk.OUTLINE),
                                       state=tk.DISABLED)
        self.btRemovePlot.pack(side='bottom')

    def update_info(self, file: CSDFile | None = None):
        if file is None:
            for attribute, variable in self._file_info.items():
                variable.set('No file selected')
            for attribute, variable in self._csd_info.items():
                variable.set('No file selected')
            self.btRemovePlot.configure(state=tk.DISABLED)
        elif not file.valid:
            for attribute, variable in self._file_info.items():
                variable.set('Invalid file')
            for attribute, variable in self._csd_info.items():
                variable.set('Invalid file')
            self.btRemovePlot.configure(state=tk.DISABLED)
        else:
            for attribute, variable in self._file_info.items():
                variable.set(str(getattr(file, attribute)))
            csd = file.csd
            if file.csd is not None:
                csd_info = CSDInfo(file.csd)
                for attribute, variable in self._csd_info.items():
                    variable.set(str(getattr(csd_info, attribute)))
            if file.plotted:
                self.btRemovePlot.configure(state=tk.NORMAL)
            else:
                self.btRemovePlot.configure(state=tk.DISABLED)
