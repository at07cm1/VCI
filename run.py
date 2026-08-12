import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

import core
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = core.VciCalculator(root)
    root.mainloop()
