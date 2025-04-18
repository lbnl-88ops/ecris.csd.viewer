import tkinter as tk

class AppMenu(tk.Menu):
    def __init__(self, owner, use_blitting: tk.BooleanVar, *args, **kwargs):
        super().__init__(owner, relief=tk.FLAT, *args, **kwargs)
        self._owner = owner
        self.create_menus(use_blitting)

    def create_menus(self, use_blitting):
        self.hamburger_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='☰', menu=self.hamburger_menu)
        self.hamburger_menu.add_checkbutton(label='Use blitting', variable=use_blitting,
                                            command=self._owner.toggle_blitting,
                                            onvalue=True, offvalue=False)
        self.hamburger_menu.add_command(label='Open diagnostic window', 
                                        command=self._owner.diagnostic_mode)
        self.hamburger_menu.add_separator()
        self.hamburger_menu.add_command(label='Quit', command=self._owner.quit)

