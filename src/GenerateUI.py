import tkinter as tk
from tkinter import messagebox

class GenerateUI:
    def __init__(self, root, vci_calculator=None):     
        self.root = root
        self.vci_calculator = vci_calculator

        self.yTop = 20
        self.xLeft = 50

        # Define application constants
        self.XREF = 5.0      # μg m⁻³
        self.ST = 5.0        # °C
        self.TTHR = 24.0     # °C

        # Calculate Button
        self.calc_btn = tk.Button(root, text="Calculate VCI", command=lambda: self.OnCalculateClicked(), 
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
            command=self.ConfirmExit,
            bg="#DC3545", fg="white", padx=10,pady=5)

        self.exit_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    def OnCalculateClicked(self):
        if self.vci_calculator:
            self.vci_calculator.CalculateVCI()
    
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
    
    def AddInputFields(self):
        vcmd = (self.root.register(self.ValidateFloat), '%P')
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
    
    def ValidateFloat(self, P):
        if P == "" or P == "-":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False
   
    def ConfirmExit(self):
        if messagebox.askyesno("Quit", "Are you sure you want to exit?"):
            try:
                self.root.destroy()
            except:
                pass

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

        for i in range(1, 16):
            lbl = tk.Label(
                self.root, 
                text=f"Equation {i}: --", 
                font=("Arial", 10),
                anchor="w"
            )
            lbl.place(x=(self.xLeft + 800), y=(self.yTop + 80 + (i - 1) * 40))
            
            # Save reference by equation number
            self.eq_labels[i] = lbl