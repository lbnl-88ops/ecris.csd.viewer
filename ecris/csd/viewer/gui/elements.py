from dataclasses import dataclass
from logging import info
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

import ttkbootstrap as ttk

from ecris.csd.viewer.analysis import Element

@dataclass
class _CustomElement:
    location: Tuple[int, int]
    element: Element
    button_frame: tk.Frame

class _CustomElementManager(tk.Frame):
    def __init__(self, owner, plot, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._max_columns = 4
        self._plot = plot
        self._custom_elements = []
    
    def add_element(self, element: Element):
        element_visibility = tk.BooleanVar(value=True)
        self._plot.add_element_indicator(element, element_visibility)
        self._plot.update()
        text = f"{element.symbol}-{element.atomic_mass}"
        element_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=2)
        button = ttk.Checkbutton(element_frame, text=text,
                                onvalue=True, offvalue=False,
                                variable=element_visibility,
                                bootstyle='round-toggle',
                                command=self._plot.update).pack(side='left', padx=5, pady=5)
        if self._custom_elements:
            last_row, last_column = self._custom_elements[-1].location 
            if last_column == self._max_columns - 1:
                column = 0
                row = last_row + 1
            else:
                column = last_column + 1
                row = last_row
        else:
            row, column = (0, 0)
        element_frame.grid(column=column, row=row)
        self._custom_elements.append(_CustomElement((row, column), element, element_frame))
        info(f'Custom elements: {len(self._custom_elements)}')
        info(f'{self} children: {len(self.winfo_children())}')

    def remove_all_elements(self):
        for custom_element in self._custom_elements:
            self._plot.remove_element_indicator(custom_element.element)
            custom_element.button_frame.grid_forget()
            custom_element.button_frame.destroy()
        self._custom_elements = []
        self._plot.update()

class ElementButtons(ttk.Frame):
    def __init__(self, owner, plot,
                 persistent_elements: List[Element], 
                 variable_elements: List[Element], 
                 *args, **kwargs):
        super().__init__(owner, padding=20, *args, **kwargs)
        self._persistent_elements = persistent_elements
        self._variable_elements = variable_elements
        self.element_visibility = {
            e: tk.BooleanVar(value=False) for e in persistent_elements + variable_elements
        }
        self._plot = plot
        self._font = "TkDefaultFont"
        self._title_font = (self._font, 14)
        self._subtitle_font = (self._font, 12)
        self._custom_elements = _CustomElementManager(self, self._plot)
        
        self.create_widgets()
        info(f'{self} children: {len(self.winfo_children())}')

    def create_widgets(self):
        lbTitle = tk.Label(self, text='Element M/Q indicators', font=self._title_font)
        lbTitle.pack(side='top')
        lbOptions = tk.Label(self, text='Display options', font=self._subtitle_font,
                             justify='left')
        lbOptions.pack(side='top', fill='x')
        button = ttk.Checkbutton(self, text='Show lines',
                                bootstyle='round-toggle',
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
            text = f"{element.symbol}-{element.atomic_mass}"
            button = ttk.Checkbutton(frElement, text=text,
                                    bootstyle='round-toggle',
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW', row=1 + i, column=0, padx=5, pady=5)
            
        lbVariable = tk.Label(frElement, text='Variable', font=self._subtitle_font,
                              justify='center')
        lbVariable.grid(column=2, row = 0, sticky='NW', columnspan=2)
        for i, element in enumerate(sorted(self._variable_elements, key=lambda e: e.atomic_number)):
            text = f"{element.symbol}-{element.atomic_mass}"
            button = ttk.Checkbutton(frElement, text=text,
                                    bootstyle='round-toggle',
                                    onvalue=True, offvalue=False,
                                    variable=self.element_visibility[element],
                                    command=self._plot.update)
            button.grid(sticky='NW', column=2, row=1+i, padx=5, pady=5)
        frElement.pack(side='top', fill='x')

        self.varSymbol = tk.StringVar()
        self.varMass = tk.StringVar()
        self.varNumber = tk.StringVar()

        lbCustom = tk.Label(self, text='Custom Elements', font=self._subtitle_font)
        lbCustom.pack(side='top')

        frCustom = tk.Frame(self)
        pad = 5
        pady = 5
        lbSymbol = tk.Label(frCustom, text='Symbol:').grid(column=0, row=0,padx=pad, pady=pady)
        entSymbol = ttk.Entry(frCustom, textvariable=self.varSymbol, width=5).grid(column=1, row=0, padx=pad, pady=pady)
        lbAtomicMass = tk.Label(frCustom, text='Mass:').grid(column=2, row=0,padx=pad, pady=pady)
        entAtomicMass = ttk.Entry(frCustom, textvariable=self.varMass, width=5).grid(column=3, row=0, padx=pad, pady=pady)
        lbAtomicNumber = tk.Label(frCustom, text='At. no.:').grid(column=4, row=0, padx=pad, pady=pady)
        entAtomicNumber = ttk.Entry(frCustom, textvariable=self.varNumber, width=5).grid(column=5, row=0, padx=pad, pady=pady)
        btAddCustom = ttk.Button(frCustom, text='Add', 
                                bootstyle=ttk.OUTLINE,
                                 command=self.add_custom_element).grid(column=6, row=0, padx=pad, pady=pady)

        frCustom.pack(side='top')
        self._custom_elements.pack(side='top')
        btnRemoveCustomElements = ttk.Button(self, text='Clear all', 
                                             bootstyle=ttk.OUTLINE,
                                            command=self._custom_elements.remove_all_elements).pack(side='top')

    def add_custom_element(self):
        e = self.get_element()
        if e is not None:
            self._custom_elements.add_element(e)
            for l in [self.varSymbol, self.varMass, self.varNumber]:
                l.set('')

        info(f'{self} children: {len(self.winfo_children())}')

    def get_element(self) -> Element:
        symbol = self.varSymbol.get()
        mass = self.varMass.get()
        number = self.varNumber.get()
        error = ''
        warning = ''
        if not mass.isdigit():
            error = 'Mass must be a valid positive integer'
        elif not number.isdigit():
            error = 'Atomic number must be a valid positive integer'
        elif int(number) > int(mass):
            error = 'Element atomic number must be less than or equal to mass'
        else:
            for element in self._persistent_elements + self._variable_elements:
                if (int(number) == element.atomic_number and int(mass) == element.atomic_mass
                    and symbol == element.symbol):
                    warning = 'Element appears to be already included in Persistent/Variable element list'
            for element in self._custom_elements._custom_elements:
                if (int(number) == element.element.atomic_number 
                    and int(mass) == element.element.atomic_mass):
                    warning = 'Element appears already included as a custom element'
        if error:
            messagebox.showerror('Error', error)
            # winError = tk.Toplevel()
            # winError.title('Error')
            # lblError = tk.Label(winError, text=f"Error with custom element input: {error}").pack()
            # b = tk.Button(winError, text="Ok", command=winError.destroy).pack()
            return None
        if warning:
            if not messagebox.askyesno('Warning', warning + '. Are you sure you want to add it?'):
                return None
        return Element(symbol, symbol, int(mass), int(number))