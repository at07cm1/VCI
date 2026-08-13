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

        # Define application constants
        self.XREF = 5.0      # μg m⁻³
        self.ST = 5.0        # °C
        self.TTHR = 24.0     # °C

        # ----- UI Elements ------
        # Calculate Button
        self.calc_btn = tk.Button(root, text="Calculate VCI", command=lambda: self.CalculateVCI(), 
                                  bg="#0D15ED", fg="white")
        self.calc_btn.place(x=(self.xLeft + 700), y=self.yTop)

        # Constant Label
        self.constant_label = tk.Label(root, text="Constant Values:", font=("Arial", 10, "bold", "underline"))
        self.constant_label.place(x=self.xLeft, y=self.yTop + 40)
        self.AddConstantsDisplay()

        # Variable Input Label
        self.variable_label = tk.Label(root, text="Variable Input:", font=("Arial", 10, "bold", "underline"))
        self.variable_label.place(x=(self.xLeft + 400), y=(self.yTop + 40))
        self.input_entries = {}
        self.AddInputFields()

        # Exit button
        self.exit_btn = tk.Button(
            self.root, text="Exit", 
            command=self.confirm_exit,
            bg="#DC3545", fg="white", padx=10,pady=5)

        self.exit_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    def AddEquationLabels(self):        
        # Results Header
        self.results_label = tk.Label(
            self.root, 
            text="Results:", 
            font=("Arial", 10, "bold", "underline")
        )
        self.results_label.place(x=(self.xLeft + 800), y=(self.yTop + 40))

        # Dictionary to store references to each equation label
        self.eq_labels = {}

        for i in range(1, 7):
            lbl = tk.Label(
                self.root, 
                text=f"Equation {i}: --", 
                font=("Arial", 10),
                anchor="w"
            )
            lbl.place(x=(self.xLeft + 800), y=(self.yTop + 80 + (i - 1) * 30))
            
            # Save reference by equation number
            self.eq_labels[i] = lbl

    def AddInputFields(self):
        vcmd = (self.root.register(self.validate_float), '%P')
        # Field definitions: (Field Name, Default Value, Units / Details)
        raw_inputs = [
            ("PM2.5", "10.0", "μg m⁻³"),
            ("Daytime heat T", "33", "°C (city T_MMT = 26, s_T = 5)"),
            ("Nighttime heat T", "26", "°C (T_thr = 24)"),
            ("NDVI", "0.45", ""),
            ("Walkability", "78", "(0–100)"),
            ("Night noise", "55", "dB(A)"),
        ]

        start_y = self.yTop + 70
        row_height = 30

        for i, (label_name, default_val, unit) in enumerate(raw_inputs):
            current_y = start_y + (i * row_height)

            # 1. Input Name Label
            lbl = tk.Label(self.root, text=label_name, font=("Arial", 9), anchor="w")
            lbl.place(x=self.xLeft + 400, y=current_y, width=130)

            # 2. Text Entry Box
            entry = tk.Entry(
                self.root, 
                font=("Arial", 9),
                validate="key",            # Trigger validation on keypress
                validatecommand=vcmd       # Call our validation function
            )
            entry.insert(0, default_val)
            entry.place(x=self.xLeft + 535, y=current_y, width=70)
            
            self.input_entries[label_name] = entry

            # 3. Unit / Context Label
            if unit:
                unit_lbl = tk.Label(self.root, text=unit, font=("Arial", 9), fg="#555555", anchor="w")
                unit_lbl.place(x=self.xLeft + 615, y=current_y)

    def AddConstantsDisplay(self):
        # Position this section to the right or below your raw inputs
        const_x = self.xLeft
        const_y = self.yTop + 40

        # List of constants to display
        constants = [
            ("X_ref", f"{self.XREF}", "μg m⁻³"),
            ("S_t", f"{self.ST}", "°C"),
            ("T_thr", f"{self.TTHR}", "°C"),
        ]

        row_height = 25
        for i, (name, value, unit) in enumerate(constants):
            current_y = const_y + 30 + (i * row_height)

            # Constant Label & Value
            txt = f"{name} = {value} {unit}"
            lbl = tk.Label(
                self.root, 
                text=txt, 
                font=("Arial", 9, "italic"), 
                fg="#333333", 
                anchor="w"
            )
            lbl.place(x=const_x, y=current_y)

    def validate_float(self, P):
        if P == "" or P == "-":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False
    
    def confirm_exit(self):
        if messagebox.askyesno("Quit", "Are you sure you want to exit?"):
            try:
                self.root.destroy()
            except:
                pass
    
    def CalculateVCI(self):
        self.process = SpecificationRules(self.root)
        try:
            pm25_val = float(self.input_entries["PM2.5"].get())
            day_heat_val = float(self.input_entries["Daytime heat T"].get())
            night_heat_val = float(self.input_entries["Nighttime heat T"].get())
            ndvi_val = float(self.input_entries["NDVI"].get())
            walkability_val = float(self.input_entries["Walkability"].get())
            night_noise_val = float(self.input_entries["Night noise"].get())
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please fill in all input fields with valid numbers.")

        self.f_pm = self.process.calculate_f_pm(pm25_val, self.XREF)
        self.f_h = self.process.calculate_f_h(day_heat_val, night_heat_val, self.ST)
        self.f_nh = self.process.calculate_f_nh(night_heat_val, self.TTHR)
                
        self.AddEquationLabels()
        
        # Update Equation labels 2, 3, and 4
        self.eq_labels[2].config(text=f"Equation 2 (f_PM): {self.f_pm:.3f}")
        self.eq_labels[3].config(text=f"Equation 3 (f_H):  {self.f_h:.2f}")
        self.eq_labels[4].config(text=f"Equation 4 (f_NH): {self.f_nh:.3f}")
