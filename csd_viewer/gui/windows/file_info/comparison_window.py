from pathlib import Path
import tkinter as tk
from typing import List
from logging import info

import numpy as np
import ttkbootstrap as ttk

from ops.ecris.drivers.venus_plc import VENUS_PLC_DATA_DEFINITIONS, GAS_NAMES
from csd_viewer.files import CSDFile
from csd_viewer.gui.windows.vertical_scroll_frame import VerticalScrolledFrame


class FileComparisonWindow(tk.Toplevel):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, takefocus=True, *args, **kwargs)
        self._font = "TkDefaultFont"
        self._subtitle_font = (self._font, 12)
        self.title("CSD File Comparison")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.files: List[CSDFile] = []
        self.geometry(owner.winfo_geometry())
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._scrolling_frame = VerticalScrolledFrame(self)
        self._scrolling_frame.grid(column=0, row=0, sticky="nsew")
        self._info_frame = self._scrolling_frame.interior
        self._info_frame.columnconfigure(0, weight=1)
        self._info_frame.rowconfigure(0, weight=1)
        self.tree_view = ttk.Treeview(self._info_frame, height=100)
        self.tree_view.grid(column=0, row=0, sticky="nsew")

    def add_files(self, paths: List[Path]) -> None:
        info(f"Adding files {paths} to comparison window")
        self.files.extend([CSDFile(p, 1) for p in paths])
        self._render_data()

    def add_file(self, path: Path) -> None:
        info(f"Adding file {path} to comparison window")
        self.files.append(CSDFile(path, 1))
        self._render_data()

    def _render_data(self) -> None:
        labels_by_category = VENUS_PLC_DATA_DEFINITIONS.labels_by_category
        for category in labels_by_category:
            self.tree_view.insert("", "end", category, text=category)
        self.tree_view["columns"] = [file.raw_timestamp for file in self.files]
        for file in self.files:
            self.tree_view.column(file.raw_timestamp, anchor=tk.E)
            self.tree_view.heading(file.raw_timestamp, text=file.formatted_datetime)
        csds = [file.csd for file in self.files]
        for category, labels in labels_by_category.items():
            for label in labels:

                def get_value(settings_dict):
                    if label.key not in settings_dict:
                        return ""
                    value = settings_dict[label.key]
                    if label.units == "boolean":
                        value = str(bool(value))
                    if label.key.startswith("gas_name"):
                        value = GAS_NAMES[int(value)]
                    return value

                units = f"({label.units})" if label.units != "nan" else ""
                values = [get_value(csd.settings) for csd in csds]
                if label.units != "boolean" and not label.key.startswith("gas_name"):
                    for i, value in enumerate(values[1:]):
                        try:
                            initial, value = float(values[0]), float(value)
                            if (
                                np.abs(value - initial)
                                / (initial if initial != 0 else 1)
                                < 0.9
                            ):
                                values[i + 1] = str(value) + " V"
                        except ValueError:
                            continue

                self.tree_view.insert(
                    category,
                    "end",
                    text=f"{label.label} {units}",
                    values=values,
                    tags="values",
                )
        return
        return
        x_padding = 10
        row_by_key = {}
        row = 1
        categories_rendered = False
        for i, file in enumerate(self.files):
            csd = file.csd
            if csd is None:
                continue
            ttk.Label(
                self._info_frame,
                text=file.timestamp,
                justify="center",
                font=(self._font, 10, "bold"),
            ).grid(column=1 + i, row=0, padx=x_padding)
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
