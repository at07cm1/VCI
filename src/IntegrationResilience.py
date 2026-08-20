
class IntegrationResilience:
    def __init__(self, root):     
            self.root = root
            self.default_allocations = {
                "NDVI": {"NEX": 0.40, "SRB": 0.30, "CEV": 0.30},
                "f_PM": {"CMX": 0.50, "SRB": 0.50},
                "NoiseNight": {"SRB": 0.50, "CMX": 0.50}
            }

            self.interaction_pairs = [
            ("CEV", "NEX"),
            ("SRB", "CMX"),
            ("SRB", "NTE"),
            ("SRB", "SEV"),
            ("CMX", "NEX")
            ]

            self.upri_defaults = {
            "Social interaction": 0.25,
            "Perceived safety": 0.35,
            "Inactivity": 0.30,
            "Commute": 0.20,
            "Housing burden": 0.25,
            "Crowding": 0.02,
            "P": 3.25,
            "H": 2.17
            }

    def CalculateVci(
        self, 
        normalized_domains = None, 
        alpha = 1/6, 
        gamma = 0.10, 
        centering_const = 0.50, 
        scale_factor = 2.0
    ):
        # Equation 13
        if normalized_domains is None:
            # Illustrative normalized V_k_tilde inputs matching Equation 13
            normalized_domains = {
                "NEX": 0.555,
                "SEV": 0.600,
                "NTE": 0.309,
                "CMX": 0.382,
                "CEV": 0.508,
                "SRB": 0.529
            }

        # 1. Main Term (Equal weights alpha = 1/6)
        main_term = alpha * sum(normalized_domains.values())

        # 2. Interaction Term (5 pairs, gamma = 0.10)
        interaction_sum = sum(
            normalized_domains[p1] * normalized_domains[p2]
            for p1, p2 in self.interaction_pairs
        )
        interaction_term = gamma * interaction_sum

        # 3. Raw VCI
        vci_raw = main_term + interaction_term

        # 4. Centering to manuscript scale
        vci_final = (vci_raw - centering_const) * scale_factor

        return {
            "main_term": main_term,
            "interaction_term": interaction_term,
            "vci_raw": vci_raw,
            "vci_final": vci_final
        }

    def AllocateSharedInput(self, raw_value, lambda_weights):
        # Equation 14
        weight_sum = sum(lambda_weights.values())
        if not abs(weight_sum - 1.0) < 1e-5:
            raise ValueError(f"Allocation fractions must sum to 1.0 (got {weight_sum}).")

        return {
            domain: weight * raw_value 
            for domain, weight in lambda_weights.items()
        }
    
    def CalculateUpri(self, inputs = None):
        # Equation 15
        if inputs is None:
            inputs = {}

        # --- Protective Inputs (P) ---
        p_dict = {
            "NDVI"              : inputs.get("NDVI", 0.45),
            "GVI"               : inputs.get("GVI", 0.30),
            "Tree canopy"       : inputs.get("Canopy", 0.25),
            "Green access"      : inputs.get("AccessGreen", 0.60),
            # Scale walkability from 0-100 to 0.0-1.0
            "Walkability"       : inputs.get("Walkability", 78.0) / 100.0,
            "Daytime light"     : inputs.get("DaytimeLight", 0.30),
            "Social interaction": self.upri_defaults["Social interaction"],
            "Perceived safety"  : self.upri_defaults["Perceived safety"],
            "P"                 : self.upri_defaults["P"]
        }

        # --- Stressor Inputs (H) ---
        h_dict = {
            "PM2.5"         : inputs.get("f_PM", 10.0) / 100.0 if inputs.get("f_PM", 10.0) > 1.0 else inputs.get("f_PM", 0.45),
            "Night noise"   : inputs.get("NoiseNight", 55.0) / 100.0 if inputs.get("NoiseNight", 55.0) > 1.0 else inputs.get("NoiseNight", 0.40),
            "Daytime heat"  : inputs.get("f_H", 33.0) / 100.0 if inputs.get("f_H", 33.0) > 1.0 else inputs.get("f_H", 0.30),
            "Night heat"    : inputs.get("f_NH", 26.0) / 100.0 if inputs.get("f_NH", 26.0) > 1.0 else inputs.get("f_NH", 0.25),
            "Inactivity"    : self.upri_defaults["Inactivity"],
            "Commute"       : self.upri_defaults["Commute"],
            "Housing burden": self.upri_defaults["Housing burden"],
            "Crowding"      : self.upri_defaults["Crowding"],
            "H"             : self.upri_defaults["H"]    
        }

        sum_p = sum(p_dict.values())
        sum_h = sum(abs(v) for v in h_dict.values())

        if sum_h == 0:
            raise ValueError("Stressor sum cannot be zero.")
        
        return sum_p / sum_h