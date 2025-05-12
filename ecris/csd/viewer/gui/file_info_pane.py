import logging
import tkinter as tk
import ttkbootstrap as ttk
from typing import Dict

from ecris.csd.analysis import CSD
from ecris.csd.viewer.files import CSDFile

_FONT = "TkDefaultFont"
_TITLE_FONT = (_FONT, 14)
_SUBTITLE_FONT = (_FONT, 12)

_INFO_BLOCKS = [
    "Vacuum (torr)", 
    "Superconductors (A)",
    "HV Voltage (V)",
    "HV Current (mA)",
    "Glaser (A)",
]

_INFO_BLOCKS_FORMATS = [
    '.1e',
    '6.2f',
    '.2f',
    '.3e',
    '.1f'
]

_INFO_BLOCKS_LABELS_AND_VALUES = [
    {'Injection': 'inj_mbar',
     'Extraction': 'ext_mbar',
     'Beam line': 'bl_mig2_torr'},
     ['inj_i', 'ext_i', 'mid_i', 'sext_i'],
     {'Extraction': 'extraction_v',
      'Puller': 'puller_v',
      'Biased Disk': 'bias_v'},
     {'Extraction': 'extraction_i',
      'Puller': 'puller_i',
      'Biased Disk': 'bias_i'},
      ['glaser_1']
]

class CSDInfoFrame(ttk.Frame):
    def __init__(self, 
                 owner, 
                 frame_title: str,
                 format: str,
                 labels_and_values: Dict[str, str],
                 *args, 
                 **kwargs):
        super().__init__(owner, *args, **kwargs)
        self.frame_title = frame_title
        self.format = format
        self.labels_and_values = labels_and_values
        self.labels: Dict = {}
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text=self.frame_title, font=_SUBTITLE_FONT).pack(side='top')
        if isinstance(self.labels_and_values, dict):
            labels = self.labels_and_values.keys()
        else:
            labels = self.labels_and_values
        for label in labels:
            frInfo = ttk.Frame(self)
            ttk.Label(frInfo, text=label).pack(side='left')
            self.labels[label] = ttk.Label(frInfo)
            self.labels[label].pack(side='right')
            frInfo.pack(fill='x')
        self.update_data_labels(None)

    def update_data_labels(self, csd: CSD | None):
        if isinstance(self.labels_and_values, dict):
            labels = self.labels_and_values.keys()
            values = self.labels_and_values.values()
        elif isinstance(self.labels_and_values, list):
            labels = self.labels_and_values
            values = self.labels_and_values
        else:
            raise ValueError('Incorrect form')

        for label, value in zip(labels, values):
            if csd is None:
                text = 'No CSD data'
            else:
                text = f'{csd.settings[value]:{self.format}}'
            self.labels[label].config(text=text)

class CSDInfo:
    def __init__(self, csd: CSD):
        self._csd = csd
        self.data_points = len(csd.time)
        self.extraction_voltage = csd.extraction_voltage

class FileInfoPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self._font = "TkDefaultFont"
        self._title_font = (self._font, 14)
        self._subtitle_font = (self._font, 12)
        self._info_widgets = []
        self._file_info = {}
        self._csd_info_frames = []
        self.visible = tk.BooleanVar(value=False)
        self.visible.trace_add('write', self.set_visible)

        self.create_widgets()

    def toggle_visibility(self):
        self.visible.set(not self.visible.get())

    def set_visible(self, *args, **kwargs):
        if not self.visible.get():
            self.pack_forget()
            self._owner.strToggleInfoText.set('>>')
        else:
            self.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            self._owner.strToggleInfoText.set('<<')

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

        for title, fmt, data in zip(_INFO_BLOCKS, _INFO_BLOCKS_FORMATS, _INFO_BLOCKS_LABELS_AND_VALUES):
            self._csd_info_frames.append(CSDInfoFrame(self, title, fmt, data))
            self._csd_info_frames[-1].pack(fill='x')

        self._controls_frame = ttk.Frame(self)

        self.btRemovePlot = ttk.Button(self._controls_frame,
                                       text="Remove from plot",
                                       bootstyle=(ttk.DANGER, ttk.OUTLINE),
                                       state=tk.DISABLED)
        self.btRemovePlot.pack(side='bottom')
        self._controls_frame.pack()

    def update_info(self, file: CSDFile | None = None):
        if file is None:
            for attribute, variable in self._file_info.items():
                variable.set('No file selected')
            self.btRemovePlot.configure(state=tk.DISABLED)
            for frame in self._csd_info_frames:
                frame.update_data_labels(None)
        elif not file.valid:
            for attribute, variable in self._file_info.items():
                variable.set('Invalid file')
            self.btRemovePlot.configure(state=tk.DISABLED)
            for frame in self._csd_info_frames:
                frame.update_data_labels(None)
        else:
            csd = file.csd
            for frame in self._csd_info_frames:
                frame.update_data_labels(csd)
            if file.plotted:
                self.btRemovePlot.configure(state=tk.NORMAL)
            else:
                self.btRemovePlot.configure(state=tk.DISABLED)
