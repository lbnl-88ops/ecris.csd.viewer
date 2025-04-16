import tkinter as tk
from typing import List

from ecris.csd.viewer.analysis import Element
from ecris.csd.viewer.gui.plot import Plot
from ecris.csd.viewer.plotting.element_indicators import ElementIndicator

class ElementButtons(tk.Frame):
    def __init__(self, owner, plot: Plot, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self.plot = plot

    def create_widgets(self):
        if self.plot.element_indicators is None:
            return
        for indicator in self.plot.element_indicators:
            is_plotted = tk.BooleanVar()
            button = tk.Checkbutton(self, text=indicator.element.name,
                                    onvalue=True, offvalue=False,
                                    variable=is_plotted,
                                    command=self.plot.update)
            button.grid(sticky='n')
            indicator.is_plotted = is_plotted
