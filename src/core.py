from logging import root
import tkinter as tk
from tkinter import messagebox

from specificationRules import SpecificationRules

class VciCalculator:
    def __init__(self, root):
        self.root = root    
        self.root.title("VCI Calculator")
        self.root.state('zoomed')

        self.yTop = 20
        self.xLeft = 50

        # ----- UI Elements ------
        # Calculate Button
        self.calc_btn = tk.Button(root, text="Calculate VCI", command=lambda: self.CalculateVCI(), 
                                  bg="#0D15ED", fg="white")
        self.calc_btn.place(x=(self.xLeft + 700), y=self.yTop)

        # Constant Label
        self.constant_label = tk.Label(root, text="Constant Values:", font=("Arial", 10, "bold", "underline"))
        self.constant_label.place(x=self.xLeft, y=self.yTop + 40)

        # Variable Input Label
        self.variable_label = tk.Label(root, text="Variable Input:", font=("Arial", 10, "bold", "underline"))
        self.variable_label.place(x=(self.xLeft + 400), y=(self.yTop + 40))

        # Exit button
        self.exit_btn = tk.Button(
            self.root, text="Exit", 
            command=self.confirm_exit,
            bg="#DC3545", fg="white", padx=10,pady=5)

        self.exit_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    def CalculateVCI(self):        
        self.AddEquationLabels(self.root)
        self.process = SpecificationRules()

    def AddEquationLabels(self, root):        
        # Results Label
        self.results_label = tk.Label(root, text="Results:", font=("Arial", 10, "bold", "underline"))
        self.results_label.place(x=(self.xLeft + 800), y=(self.yTop + 40))

        # Equation Labels
        for i in range(1, 7):
            equation_label = tk.Label(root, text=f"Equation {i}:", font=("Arial", 10))
            equation_label.place(x=(self.xLeft + 800), y=(self.yTop + 80 + (i - 1) * 30))

    def confirm_exit(self):
        if messagebox.askyesno("Quit", "Are you sure you want to exit?"):
            try:
                self.root.destroy()
            except:
                pass