from cProfile import label
import tkinter as tk
from typing import List

from ecris.csd.viewer.analysis import Element

class ElementButtons(tk.Frame):
    def __init__(self, owner, plot,
                 persistent_elements: List[Element], 
                 variable_elements: List[Element], 
                 *args, **kwargs):
        super().__init__(owner, relief=tk.GROOVE, 
                         padx=20, pady=20, borderwidth=5, *args, **kwargs)
        self._persistent_elements = persistent_elements
        self._variable_elements = variable_elements
        self.element_visibility = {
            e: tk.BooleanVar(value=False) for e in persistent_elements + variable_elements
        }
        self._plot = plot
        self._font = "TkDefaultFont"
        self._title_font = (self._font, 14)
        self._subtitle_font = (self._font, 12)
        
        self.create_widgets()

    def create_widgets(self):
        lbTitle = tk.Label(self, text='Element M/Q indicators', font=self._title_font)
        lbTitle.pack(side='top')
        lbOptions = tk.Label(self, text='Display options', font=self._subtitle_font,
                             justify='left')
        lbOptions.pack(side='top', fill='x')
        button = tk.Checkbutton(self, text='Show lines',
                                onvalue=True, offvalue=False,
                                variable=self._plot.draw_element_lines,
                                command=self._plot.update)
        button.pack(side='top')
        frElement = tk.Frame(self)
        frElement.columnconfigure(0, weight=1)
        frElement.columnconfigure(2, weight=1)
        frElement.columnconfigure(3, weight=1)
        frElement.columnconfigure(4, weight=1)
        lbPersistent = tk.Label(frElement, text='Persistent', font=self._subtitle_font,
                                justify='center')
        lbPersistent.grid(column=0, row=0, sticky='NW', columnspan=2)
        for i, element in enumerate(sorted(self._persistent_elements, key=lambda e: e.atomic_number)):
            text = f"{element.symbol}-{element.atomic_weight}"
            button = tk.Checkbutton(frElement, text=text,
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW', row=1 + i, column=0)
            
        lbVariable = tk.Label(frElement, text='Variable', font=self._subtitle_font,
                              justify='center')
        lbVariable.grid(column=2, row = 0, sticky='NW', columnspan=2)
        for i, element in enumerate(sorted(self._variable_elements, key=lambda e: e.atomic_number)):
            text = f"{element.symbol}-{element.atomic_weight}"
            button = tk.Checkbutton(frElement, text=text,
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW', column=2, row=1+i)
        frElement.pack(side='top', fill='x')

        self.varSymbol = tk.StringVar()
        self.varMass = tk.StringVar()
        self.varNumber = tk.StringVar()

        lbCustom = tk.Label(self, text='Custom Elements', font=self._subtitle_font)
        lbCustom.pack(side='top')

        frCustom = tk.Frame(self)
        lbSymbol = tk.Label(frCustom, text='Symbol:').grid(column=0, row=0)
        entSymbol = tk.Entry(frCustom, textvariable=self.varSymbol, width=5).grid(column=1, row=0)
        lbAtomicWeight = tk.Label(frCustom, text='Mass:').grid(column=2, row=0)
        entAtomicWeight = tk.Entry(frCustom, textvariable=self.varMass, width=5).grid(column=3, row=0)
        lbAtomicNumber = tk.Label(frCustom, text='Number:').grid(column=4, row=0)
        entAtomicNumber = tk.Entry(frCustom, textvariable=self.varNumber, width=5).grid(column=5, row=0)
        btAddCustom = tk.Button(frCustom, text='Add',
                                command=self.add_custom_element).grid(column=6, row=0)

        frCustom.pack(side='top')

    def add_custom_element(self):
        e = Element(self.varSymbol.get(), self.varSymbol.get(), int(self.varMass.get()), int(self.varNumber.get()))
        self.element_visibility[e] = tk.BooleanVar(value=True)
        self._plot.add_element_indicator(e, self.element_visibility[e])
        self._plot.update()
