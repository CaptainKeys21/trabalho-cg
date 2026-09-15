import tkinter as tk
from tkinter import ttk

from views.Viewport import Viewport
from views.SideMenu import SideMenu
# import numpy as np

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Viewport 2D")
        self.geometry("1000x800")
        # np.set_printoptions(legacy='1.25')
        # Container principal
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        viewport = Viewport(container)
        viewport.pack(side="right", padx=20, pady=20)

        painel = SideMenu(container, viewport)
        painel.pack(side="left", fill="y", padx=5, pady=5)

if __name__ == "__main__":
    app = App()
    app.mainloop()