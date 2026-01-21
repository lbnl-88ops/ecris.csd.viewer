from pathlib import Path
import tkinter as tk
from typing import List
from logging import info

import ttkbootstrap as ttk

from ops.ecris.drivers.venus_plc import VENUS_PLC_DATA_DEFINITIONS, GAS_NAMES
from csd_viewer.files import CSDFile
from csd_viewer.gui.windows.vertical_scroll_frame import VerticalScrolledFrame


class FileComparisonWindow(tk.Toplevel):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, takefocus=True)
        self._font = "TkDefaultFont"
        self._subtitle_font = (self._font, 12)
        self.title("CSD File Comparison")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.files: List[CSDFile] = []
        self.create_widgets()

    def create_widgets(self):
        self._scrolling_frame = VerticalScrolledFrame(self)
        self._info_frame = self._scrolling_frame.interior
        self._scrolling_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE)

    def add_files(self, paths: List[Path]) -> None:
        info(f"Adding files {paths} to comparison window")
        self.files.extend([CSDFile(p, 1) for p in paths])
        self._render_data()

    def add_file(self, path: Path) -> None:
        info(f"Adding file {path} to comparison window")
        self.files.append(CSDFile(path, 1))
        self._render_data()

    def _render_data(self) -> None:
        x_padding = 10
        row_by_key = {}
        row = 1
        categories_rendered = False
        for i, file in enumerate(self.files):
            csd = file.csd
            if csd is None:
                continue
            ttk.Label(self._info_frame, text=file.timestamp, justify="center").grid(
                column=1 + i, row=0, padx=x_padding
            )
            for (
                category,
                labels,
            ) in VENUS_PLC_DATA_DEFINITIONS.labels_by_category.items():
                if not categories_rendered:
                    ttk.Label(
                        self._info_frame,
                        text=category,
                        justify="left",
                        font=self._subtitle_font,
                    ).grid(column=0, row=row, sticky="W", padx=x_padding, pady=(10, 0))
                    row += 1
                for label in labels:
                    if label.key not in row_by_key:
                        row_by_key[label.key] = row
                        label_row = row
                        units = f"({label.units})" if label.units != "nan" else ""
                        ttk.Label(
                            self._info_frame,
                            text=f"{label.label} {units}",
                            justify="left",
                        ).grid(column=0, row=row, sticky="W", padx=x_padding)
                        row += 1
                    else:
                        label_row = row_by_key[label.key]
                    if label.key in csd.settings:
                        value = csd.settings[label.key]
                        if label.units == "boolean":
                            value = str(bool(int(value)))
                        if label.key.startswith("gas_name"):
                            value = GAS_NAMES[int(value)]
                        ttk.Label(
                            self._info_frame,
                            text=value,
                            justify="right",
                        ).grid(column=1 + i, row=label_row, sticky="e")
            categories_rendered = True

    def on_close(self):
        self.destroy()
