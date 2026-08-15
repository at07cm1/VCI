from logging import root
import tkinter as tk
from tkinter import messagebox

from IntegrationResilience import IntegrationResilience
from UrbanVitalSigns import UrbanVitalSigns
from SpecificationRules import SpecificationRules

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
        self.urbanVitalSigns = UrbanVitalSigns(self.root)
        self.IntegrationResilience = IntegrationResilience(self.root)
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
        self.f_h  = self.process.calculate_f_h(day_heat_val, night_heat_val, self.ST)
        self.f_nh = self.process.calculate_f_nh(night_heat_val, self.TTHR)

        anchors = {
            "f_PM":        (1.20, 0.30),
            "f_H":         (1.50, 0.80),
            "f_NH":        (1.00, 1.20),
            "NDVI":        (0.40, 0.12),
            "Walkability": (60.0, 15.0),
            "NoiseNight":  (50.0, 6.0),
        }

        # 4. Step 3 Standardisation (Calculate Z-scores)
        z_scores = {
            "f_PM":        self.process.calculate_z_score(self.f_pm, *anchors["f_PM"]),
            "f_H":         self.process.calculate_z_score(self.f_h, *anchors["f_H"]),
            "f_NH":        self.process.calculate_z_score(self.f_nh, *anchors["f_NH"]),
            "NDVI":        self.process.calculate_z_score(ndvi_val, *anchors["NDVI"]),
            "Walkability": self.process.calculate_z_score(walkability_val, *anchors["Walkability"]),
            "NoiseNight":  self.process.calculate_z_score(night_noise_val, *anchors["NoiseNight"]),
        }
        
        nex_raw = self.urbanVitalSigns.calculate_nex(z_scores['NDVI'], other_z_values=[0.20]*6)
        nte_raw = self.urbanVitalSigns.calculate_nte(z_noise=z_scores['NoiseNight'], z_nh=z_scores['f_NH'] )

        # Step 5
        # Sign Orientation
        nex_oriented = self.process.apply_orientation(nex_raw, is_cmx=False)
        nte_oriented = self.process.apply_orientation(nte_raw, is_cmx=False)

        #Normalization on [0, 1] using fixed bounds (alpha = -2, beta = +2)
        nex_norm_raw = self.process.normalize_vital_sign(nex_oriented, alpha=-2.0, beta=2.0)
        nte_norm_raw = self.process.normalize_vital_sign(nte_oriented, alpha=-2.0, beta=2.0)

        # Step 6
        normalized_domains = {
            "NEX": nex_norm_raw,   # 0.56 (from Step 5)
            "SEV": 0.60,        # Illustrative fixed value
            "NTE": nte_norm_raw,   # 0.31 (from Step 5)
            "CMX": 0.38,        # Illustrative fixed value
            "CEV": 0.52,        # Illustrative fixed value
            "SRB": 0.49,        # Illustrative fixed value
        }

        #Calculate VCI (Raw and Centered)
        vci_raw, vci_centered_raw = self.IntegrationResilience.calculate_vci(
            normalized_domains=normalized_domains,
            alpha_k=1/6,
            gamma=0.10,
            interaction_sum=1.35,
            centering_const=0.50
        )

        self.AddEquationLabels()
        
        # Update Equation Labels 2, 3, and 4 for step 2
        self.eq_labels[2].config(text=f"Equation 2 (f_PM): {self.f_pm:.3f}")
        self.eq_labels[3].config(text=f"Equation 3 (f_H):  {self.f_h:.2f}")
        self.eq_labels[4].config(text=f"Equation 4 (f_NH): {self.f_nh:.3f}")

        # Update Equation Label 1 for Step 3 Standardisation (Z-scores)
        z_text = (
            f"Equation 1 (Z-scores):\n"
            f"  • Z_PM: {z_scores['f_PM']:+.2f} | Z_H: {z_scores['f_H']:+.3f} | Z_NH: {z_scores['f_NH']:+.2f}"
            f"  • Z_NDVI: {z_scores['NDVI']:+.2f} | Z_Walk: {z_scores['Walkability']:+.2f} | Z_Noise: {z_scores['NoiseNight']:+.2f}"
        )

        self.eq_labels[1].config(text=z_text, justify="left")

        # Update Equation Labels 7 and 9 for Step 4 NEX Calculation
        self.eq_labels[7].config(text=f"Equation 7 (NEX):  {nex_raw:+.2f}")
        self.eq_labels[9].config(text=f"Equation 9 (NTE):  {nte_raw:+.2f}")

        # Update Equation Labels 5 and 6 for Step 5 Orient and scale
        self.eq_labels[5].config(text=f"Eq 5 (NEX~): {nex_norm_raw:.2f}")
        self.eq_labels[6].config(text=f"Eq 6 (NTE~): {nte_norm_raw:.2f}")

        # Update Equation Labels 13 for Step 6 Integration
        self.eq_labels[13].config(text=f"Equation 13 (VCI_raw): {vci_raw:.3f} | VCI_centered: {vci_centered_raw:.3f}")
