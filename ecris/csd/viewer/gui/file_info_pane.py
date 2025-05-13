import logging
from dataclasses import dataclass
import tkinter as tk
import ttkbootstrap as ttk
from typing import Dict, List, Optional

from ecris.csd.analysis import CSD
from ecris.csd.viewer.files import CSDFile

_FONT = "TkDefaultFont"
_TITLE_FONT = (_FONT, 14)
_SUBTITLE_FONT = (_FONT, 12)
_COLUMN_FONT = (_FONT, 10)


class CSDInfoRow:
    def __init__(self, csd_settings: str | List[str], formats: str | List[str], info_label: Optional[str] = ''):
        if isinstance(csd_settings, str):
            if info_label is None:
                info_label = csd_settings
            csd_settings = [csd_settings]
        if isinstance(formats, str):
            formats = [formats]
        if len(formats) != len(csd_settings):
            raise RuntimeError('Length of formats and csd settings must be the same')
        self.csd_settings = csd_settings
        self.formats = formats
        self.info_label = info_label

class CSDInfoBlock(ttk.Label):
    def __init__(self, owner: ttk.Frame, csd_setting: str, format: str):
        super().__init__(owner, relief=ttk.RAISED, borderwidth=2
                      
                         )
        self.csd_setting = csd_setting
        self.format = format
    
    def update(self, csd: Optional[CSD] = None):
        text = 'No CSD Data'
        if csd is not None:
            text = f'{csd.settings[self.csd_setting]:{self.format}}'
        self.config(text=text)

_FRAMES = [
    'Vacuum',
    ]
_COLUMNS = [
    ['(torr)']
    ]
_INFO_ROWS = [
    [
        CSDInfoRow('inj_mbar', '.1e', 'Injection'),
        CSDInfoRow('ext_mbar', '.1e', 'Extraction'),
        CSDInfoRow('bl_mig2_torr', '.1e', 'Beam line'),
    ]
]


class CSDInfoFrame(ttk.Frame):
    def __init__(self, owner, frame_title: str, 
                 csd_info_rows: CSDInfoRow | List[CSDInfoRow], 
                 column_titles: List[str] | None):
        super().__init__(owner, relief=ttk.RAISED)
        self.frame_title = frame_title
        if not isinstance(csd_info_rows, list):
            csd_info_rows = [csd_info_rows]
        if column_titles is None:
            column_titles = []
        self.info_rows = csd_info_rows
        self.column_titles = column_titles
        self.info_blocks = []
        self.create_widgets()
        self.update_csd_info()

    def create_widgets(self):
        grid_width = 1 + max(len(row.csd_settings) for row in self.info_rows)
        row_start = 1 if self.column_titles is None else 2
        ttk.Label(self, text=self.frame_title, font=_SUBTITLE_FONT,
                    relief=ttk.RAISED, borderwidth=2,
                  ).grid(row=0, column=0,
                                                                         columnspan=grid_width)
        for i, title in enumerate(self.column_titles):
            ttk.Label(self, text=title, font=_COLUMN_FONT, 
                    relief=ttk.RAISED, borderwidth=2,
                      ).grid(row=1, column=1 + i)

        for i, row in enumerate(self.info_rows):
            n_row = row_start + i
            ttk.Label(self, text=row.info_label,
                    relief=ttk.RAISED, borderwidth=2,
                      ).grid(row=n_row, column=0, 
                                                      sticky='w')
            for j, setting in enumerate(row.csd_settings):
                self.info_blocks.append(CSDInfoBlock(self, setting, row.formats[j]))
                self.info_blocks[-1].grid(row=n_row, column = j + 1, 
                                          sticky='ew')

    def update_csd_info(self, csd: CSD | None = None):
        for info_block in self.info_blocks:
            info_block.update(csd)

class FileInfoPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self._font = "TkDefaultFont"
        self._title_font = (self._font, 14)
        self._subtitle_font = (self._font, 12)
        self._info_widgets = []
        self._file_info = {}
        self._csd_info_frames: List[CSDInfoFrame] = []
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
        self.canvas = ttk.Canvas(self)
        tk.Label(self.canvas, text='File Info', font=self._title_font).pack()
        self._info_frame = ttk.Frame(self.canvas)
        for i, (name, attribute) in enumerate(zip(['Filename', 'Time Stamp'], 
                                                  ['filename', 'timestamp'])):
            self._file_info[attribute] = tk.StringVar(value='No file selected')
            frInfo = ttk.Frame(self.canvas)
            ttk.Label(frInfo, text=name).pack(side='left')
            ttk.Label(frInfo, textvariable=self._file_info[attribute]).pack(side='right')
            frInfo.pack(fill='x')
        self._info_frame.pack()
        
        tk.Label(self.canvas, text='CSD Info', font=self._title_font).pack()

        for title, csd_info_rows, column_titles in zip(_FRAMES, _INFO_ROWS, _COLUMNS):
            self._csd_info_frames.append(CSDInfoFrame(self.canvas, 
                                                      title, csd_info_rows, column_titles))
            self._csd_info_frames[-1].pack(fill='x')

        self.scrollbar = ttk.Scrollbar(self, orient='vertical')
        self.canvas.pack(side='left', fill='both', padx=10)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')

        self._controls_frame = ttk.Frame(self)

        self._controls_frame.pack()

    def update_info(self, file: CSDFile | None = None):
        if file is None:
            for attribute, variable in self._file_info.items():
                variable.set('No file selected')
            for frame in self._csd_info_frames:
                frame.update_csd_info()
        elif not file.valid:
            for attribute, variable in self._file_info.items():
                variable.set('Invalid file')
            for frame in self._csd_info_frames:
                frame.update_csd_info()
        else:
            for attribute, variable in self._file_info.items():
                variable.set(getattr(file, attribute))
            csd = file.csd
            for frame in self._csd_info_frames:
                frame.update_csd_info(csd)
