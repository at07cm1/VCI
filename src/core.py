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
            "GVI":         (0.28, 0.10),
            "AccessGreen": (0.50, 0.20),
            "Canopy":      (0.30, 0.12),
            "Blue":        (0.25, 0.15),
            "Micro":       (0.35, 0.15),
            "Sidewalk":    (0.55, 0.18),
            "Walkability": (60.0, 15.0),
            "NoiseNight":  (50.0, 6.0)
        }

        # 4. Step 3 Standardisation (Calculate Z-scores)
       

        raw_values = {
        "f_PM"        : self.f_pm,
        "f_H"         : self.f_h,
        "f_NH"        : self.f_nh,
        "NDVI"        : ndvi_val,
        "GVI"         : gvi_val,
        "AccessGreen" : access_green,
        "Canopy"      : canopy_val,
        "Blue"        : blue_val,
        "Micro"       : micro_val,
        "Sidewalk"    : sidewalk_val,
        "Walkability" : walkability_val,
        "NoiseNight"  : night_noise_val,
        }

        # Standardise all variables dynamically
        z_scores = {
            key: self.process.Calculate_ZScore(val, *anchors[key])
            for key, val in raw_values.items()
            if key in anchors
        }

        # Equations 7 - 12 Calculations        
        nex_raw = self.urbanVitalSigns.CalculateNex(z_scores)
        sev_raw = self.urbanVitalSigns.CalculateSev()
        nte_raw = self.urbanVitalSigns.CalculateNte(z_noise = z_scores['NoiseNight'], z_nh = z_scores['f_NH'] )
        cmx_raw = self.urbanVitalSigns.CalculateCmx(z_f_pm = z_scores['f_PM'], z_f_h = z_scores['f_H'])
        cev_raw = self.urbanVitalSigns.CalculateCev(z_sum = 2.25) # 2.25 is illustrative value

        p_components = [z_scores["NDVI"], z_scores["Walkability"], 0.40, 0.33]
        h_components = [z_scores["f_PM"], z_scores["NoiseNight"], z_scores["f_H"]]

        srb_raw = self.urbanVitalSigns.CalculateSrb(
                    protective_list = p_components, 
                    adverse_list = h_components
                )
        
        # Steps 5 & 6 in a single comprehension pass
        raw_domains = {
            "NEX": nex_raw, "SEV": sev_raw, "NTE": nte_raw,
            "CMX": cmx_raw, "CEV": cev_raw, "SRB": srb_raw
        }
        
        normalized_domains = {
            name: self.process.NormalizeVitalSign(
                self.process.ApplyOrientation(val, is_cmx=(name == "CMX")),
                alpha=-2.0,
                beta=2.0
            )
            for name, val in raw_domains.items()
        }

        ndvi_allocations = self.IntegrationResilience.AllocateSharedInput(
            raw_value = inputs.get("NDVI", 0.45), 
            lambda_weights = self.IntegrationResilience.default_allocations["NDVI"]
        )

        #Calculate VCI (Raw and Centered)
        vci_results = self.IntegrationResilience.CalculateVci(
            normalized_domains = normalized_domains)

        vci_raw = vci_results["vci_raw"]
        vci_centered_raw = vci_results["vci_final"]

        # Step 7: Calculate UPRI
        upri_raw = self.IntegrationResilience.CalculateUpri(inputs = inputs)
        state_enum = self.IntegrationResilience.ResultClassification(vci = vci_centered_raw, upri = upri_raw)

        self.generateUI.AddEquationLabels()
        
        # Update Equation Labels 2, 3, and 4 for step 2
        self.generateUI.eq_labels[2].config(text=f"Equation 2 (f_PM): {self.f_pm:.3f}")
        self.generateUI.eq_labels[3].config(text=f"Equation 3 (f_H):  {self.f_h:.2f}")
        self.generateUI.eq_labels[4].config(text=f"Equation 4 (f_NH): {self.f_nh:.3f}")

        # Update Equation Label 1 for Step 3 Standardisation (Z-scores)
        z_text = (
            f"Equation 1 (Z-scores):\n"
            f"  • Z_PM: {z_scores['f_PM']:+.2f} | Z_H: {z_scores['f_H']:+.2f} | Z_NH: {z_scores['f_NH']:+.2f}"
            f"  • Z_NDVI: {z_scores['NDVI']:+.2f} | Z_GVI: {z_scores['GVI']:+.2f} | Z_AccessGreen: {z_scores['AccessGreen']:+.2f}\n"
            f"  • Z_Canopy: {z_scores['Canopy']:+.2f} | • Z_Blue: {z_scores['Blue']:+.2f} | Z_Micro: {z_scores['Micro']:+.2f} | Z_Sidewalk: {z_scores['Sidewalk']:+.2f} | Z_Walk: {z_scores['Walkability']:+.2f} | Z_Noise: {z_scores['NoiseNight']:+.2f}"
        )

        self.generateUI.eq_labels[1].config(text=z_text, justify="left")

        # Update Equation Labels 7, 8 and 9 for Step 4 NEX Calculation
        self.generateUI.eq_labels[7].config(text=f"Equation 7 (NEX):  {nex_raw:+.3f}")
        self.generateUI.eq_labels[8].config(text=f"Equation 8 (SEV):  {sev_raw:+.3f}")
        self.generateUI.eq_labels[9].config(text=f"Equation 9 (NTE):  {nte_raw:+.3f}")

        # Update Equation Labels 10, 11 and 12for CMX, CEV and SRB Calculation
        self.generateUI.eq_labels[10].config(text=f"Equation 10 (CMX):  {cmx_raw:+.3f}")
        self.generateUI.eq_labels[11].config(text=f"Equation 11 (CEV):  {cev_raw:+.3f}")
        self.generateUI.eq_labels[12].config(text=f"Equation 12 (SRB):  {srb_raw:+.3f}")

        # Update Equation Labels 5 and 6 for Step 5 Orient and scale
        self.generateUI.eq_labels[5].config(text=f"Equation 5, 6: NEX: {normalized_domains['NEX']:.3f} | SEV: {normalized_domains['SEV']:.3f} | NTE: {normalized_domains['NTE']:.3f}")
        self.generateUI.eq_labels[6].config(text=f"Equation 5, 6: CMX: {normalized_domains['CMX']:.3f} | CEV: {normalized_domains['CEV']:.3f} | SRB: {normalized_domains['SRB']:.3f}")

        # Update Equation Labels 13 and 14 for Step 6 Integration
        self.generateUI.eq_labels[13].config(text=f"Equation 13 (VCI_raw): {vci_raw:.3f} | VCI_centered: {vci_centered_raw:.3f}")
        self.generateUI.eq_labels[14].config(text=f"Equation 14 (NDVI Allocations): NEX: {ndvi_allocations['NEX']:.3f} | SRB: {ndvi_allocations['SRB']:.3f} | CEV: {ndvi_allocations['CEV']:.3f}")

        # Update Equation Labels 15 for Step 7 UPRI Calculation
        self.generateUI.eq_labels[15].config(text=f"Eq 15 (UPRI): {upri_raw:.3f}")

        # Update Classification Label
        self.generateUI.eq_labels[16].config(
            text=f"City State Classification: {state_enum.value.upper()}"
        )