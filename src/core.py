from logging import root
import tkinter as tk

from IntegrationResilience import IntegrationResilience
from UrbanVitalSigns import UrbanVitalSigns
from SpecificationRules import SpecificationRules
from GenerateUI import GenerateUI

class VciCalculator:
    def __init__(self, root):
        self.root = root    
        self.root.title("VCI Calculator")
        self.root.state('zoomed')

        # ----- Generate UI Elements ------
        self.generateUI = GenerateUI(self.root, vci_calculator=self)
    
    def CalculateVCI(self):
        self.process = SpecificationRules(self.root)
        self.urbanVitalSigns = UrbanVitalSigns(self.root)
        self.IntegrationResilience = IntegrationResilience(self.root)
        try:
            inputs = {key: float(entry.get()) for key, entry in self.generateUI.input_entries.items()}

            pm25_val        = inputs["PM2.5"]
            day_heat_val    = inputs["T_day"]
            night_heat_val  = inputs["T_night"]
            ndvi_val        = inputs["NDVI"]
            gvi_val         = inputs["GVI"]
            access_green    = inputs["AccessGreen"]
            canopy_val      = inputs["Canopy"]
            blue_val        = inputs["Blue"]
            micro_val       = inputs["Micro"]
            sidewalk_val    = inputs["Sidewalk"]
            walkability_val = inputs["Walkability"]
            night_noise_val = inputs["NoiseNight"]

        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please fill in all input fields with valid numbers.")

        self.f_pm = self.process.Calculate_Fpm(pm25_val, self.generateUI.XREF)
        self.f_h  = self.process.Calculate_Fh(day_heat_val, night_heat_val, self.generateUI.ST)
        self.f_nh = self.process.Calculate_Fnh(night_heat_val, self.generateUI.TTHR)

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
            "f_PM":        self.process.Calculate_ZScore(self.f_pm, *anchors["f_PM"]),
            "f_H":         self.process.Calculate_ZScore(self.f_h, *anchors["f_H"]),
            "f_NH":        self.process.Calculate_ZScore(self.f_nh, *anchors["f_NH"]),
            "NDVI":        self.process.Calculate_ZScore(ndvi_val, *anchors["NDVI"]),
            "Walkability": self.process.Calculate_ZScore(walkability_val, *anchors["Walkability"]),
            "NoiseNight":  self.process.Calculate_ZScore(night_noise_val, *anchors["NoiseNight"]),
        }
        
        nex_raw = self.urbanVitalSigns.CalculateNex(z_scores['NDVI'], other_z_values=[0.20]*6)
        nte_raw = self.urbanVitalSigns.CalculateNte(z_noise=z_scores['NoiseNight'], z_nh=z_scores['f_NH'] )

        # Step 5
        # Sign Orientation
        nex_oriented = self.process.ApplyOrientation(nex_raw, is_cmx=False)
        nte_oriented = self.process.ApplyOrientation(nte_raw, is_cmx=False)

        # Normalization on [0, 1] using fixed bounds (alpha = -2, beta = +2)
        nex_norm_raw = self.process.NormalizeVitalSign(nex_oriented, alpha=-2.0, beta=2.0)
        nte_norm_raw = self.process.NormalizeVitalSign(nte_oriented, alpha=-2.0, beta=2.0)

        # Step 6
        normalized_domains = {
            "NEX": nex_norm_raw, # 0.56 (from Step 5)
            "SEV": 0.60,         # Illustrative fixed value
            "NTE": nte_norm_raw, # 0.31 (from Step 5)
            "CMX": 0.38,         # Illustrative fixed value
            "CEV": 0.52,         # Illustrative fixed value
            "SRB": 0.49,         # Illustrative fixed value
        }

        #Calculate VCI (Raw and Centered)
        vci_raw, vci_centered_raw = self.IntegrationResilience.CalculateVci(
            normalized_domains=normalized_domains,
            alpha_k=1/6,
            gamma=0.10,
            interaction_sum=1.35,
            centering_const=0.50
        )

        # Step 7: Calculate UPRI
        sum_p = 2.10
        sum_h = 2.55

        upri_raw = self.IntegrationResilience.CalculateUpri(sum_protective=sum_p, sum_stressors=sum_h)

        self.generateUI.AddEquationLabels()
        
        # Update Equation Labels 2, 3, and 4 for step 2
        self.generateUI.eq_labels[2].config(text=f"Equation 2 (f_PM): {self.f_pm:.3f}")
        self.generateUI.eq_labels[3].config(text=f"Equation 3 (f_H):  {self.f_h:.2f}")
        self.generateUI.eq_labels[4].config(text=f"Equation 4 (f_NH): {self.f_nh:.3f}")

        # Update Equation Label 1 for Step 3 Standardisation (Z-scores)
        z_text = (
            f"Equation 1 (Z-scores):\n"
            f"  • Z_PM: {z_scores['f_PM']:+.2f} | Z_H: {z_scores['f_H']:+.3f} | Z_NH: {z_scores['f_NH']:+.2f}"
            f"  • Z_NDVI: {z_scores['NDVI']:+.2f} | Z_Walk: {z_scores['Walkability']:+.2f} | Z_Noise: {z_scores['NoiseNight']:+.2f}"
        )

        self.generateUI.eq_labels[1].config(text=z_text, justify="left")

        # Update Equation Labels 7 and 9 for Step 4 NEX Calculation
        self.generateUI.eq_labels[7].config(text=f"Equation 7 (NEX):  {nex_raw:+.2f}")
        self.generateUI.eq_labels[9].config(text=f"Equation 9 (NTE):  {nte_raw:+.2f}")

        # Update Equation Labels 5 and 6 for Step 5 Orient and scale
        self.generateUI.eq_labels[5].config(text=f"Eq 5 (NEX~): {nex_norm_raw:.2f}")
        self.generateUI.eq_labels[6].config(text=f"Eq 6 (NTE~): {nte_norm_raw:.2f}")

        # Update Equation Labels 13 for Step 6 Integration
        self.generateUI.eq_labels[13].config(text=f"Equation 13 (VCI_raw): {vci_raw:.3f} | VCI_centered: {vci_centered_raw:.3f}")

        # Update Equation Labels 15 for Step 7 UPRI Calculation
        self.generateUI.eq_labels[15].config(text=f"Eq 15 (UPRI): {upri_raw:.2f}")