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
        lbTitle = tk.Label(self, text='Element M/Q indicators')
        lbTitle.grid(sticky='N', column=0, row=0, columnspan=2)
        button = tk.Checkbutton(self, text='Show lines',
                                onvalue=True, offvalue=False,
                                variable=self._plot.draw_element_lines,
                                command=self._plot.update)
        button.grid(sticky='S', column=0, row=1)
        lbPersistent = tk.Label(self, text='Persistent')
        lbPersistent.grid(sticky='N', column=0, row=2)
        for i, element in enumerate(sorted(self._persistent_elements, key=lambda e: e.atomic_number)):
            text = f"{element.symbol}-{element.atomic_weight}"
            button = tk.Checkbutton(self, text=text,
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW', row=3+i, column=0)
            
        lbVariable = tk.Label(self, text='Variable')
        lbVariable.grid(sticky='N', column=1, row = 2)
        for i, element in enumerate(sorted(self._variable_elements, key=lambda e: e.atomic_number)):
            text = f"{element.symbol}-{element.atomic_weight}"
            button = tk.Checkbutton(self, text=text,
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW', column=1, row=3+i)
