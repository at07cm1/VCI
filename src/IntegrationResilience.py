from enum import Enum

class CityState(Enum):
    VITAL    = "Vital"
    STRESSED = "Stressed"
    FRAGILE  = "Fragile"
    CRITICAL = "Critical"

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

        # Protective inputs (P): keep raw values and avoid the percent-scaling
        # adjustments that were introduced in the recent change.
        p_dict = {
            "NDVI": inputs.get("NDVI", 0.45),
            "GVI": inputs.get("GVI", 0.30),
            "Tree canopy": inputs.get("Canopy", 0.25),
            "Green access": inputs.get("AccessGreen", 0.60),
            "Walkability": inputs.get("Walkability", 78.0),
            "Daytime light": inputs.get("DaytimeLight", 0.15),
            "Social interaction": self.upri_defaults["Social interaction"],
            "Perceived safety": self.upri_defaults["Perceived safety"],
            "P": self.upri_defaults["P"]
        }

        # Stressor inputs (H): keep the direct value scale from the original model.
        h_dict = {
            "PM2.5"         : inputs.get("PM2.5", 25.0),
            "Night noise"   : inputs.get("NoiseNight", 55.0),
            "Daytime heat"  : inputs.get("T_day", 33.0),
            "Night heat"    : inputs.get("T_night", 26.0),
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

    def ResultClassification(self, vci, upri):
        """
        Classifies urban state using VCI and UPRI score thresholds.
        Returns a CityState Enum instance.
        """
        if vci > 0 and upri > 1.5:
            return CityState.VITAL
        elif vci >= 0 and (1.0 < upri <= 1.5):
            return CityState.STRESSED
        elif vci < 0 and (0.5 < upri <= 1.0):
            return CityState.FRAGILE
        elif vci < 0 and upri <= 0.5:
            return CityState.CRITICAL
        else:
            # Boundary fallback checks
            if upri > 1.5:
                return CityState.VITAL
            elif upri > 1.0:
                return CityState.STRESSED
            elif upri > 0.5:
                return CityState.FRAGILE
            else:
                return CityState.CRITICAL