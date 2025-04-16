import tkinter as tk
from typing import List

from ecris.csd.viewer.analysis import Element

class ElementButtons(tk.Frame):
    def __init__(self, owner, plot,
                 persistent_elements: List[Element], 
                 variable_elements: List[Element], 
                 *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._persistent_elements = persistent_elements
        self._variable_elements = variable_elements
        self.element_visibility = {
            e: tk.BooleanVar(value=False) for e in persistent_elements + variable_elements
        }
        self._plot = plot
        self.create_widgets()

    def create_widgets(self):
        lbPersistent = tk.Label(self, text='Persistent elements')
        lbPersistent.grid(sticky='N')
        for element in sorted(self._persistent_elements, key=lambda e: e.atomic_number):
            text = f"{element.symbol}-{element.atomic_weight}"
            button = tk.Checkbutton(self, text=text,
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW')
            
        lbVariable = tk.Label(self, text='Variable elements')
        lbVariable.grid(sticky='N')
        for element in sorted(self._variable_elements, key=lambda e: e.atomic_number):
            text = f"{element.symbol}-{element.atomic_weight}"
            button = tk.Checkbutton(self, text=text,
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW')