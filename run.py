import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

import Core
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = Core.VciCalculator(root)
    root.mainloop()
