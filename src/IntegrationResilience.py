
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
            "Crowding": 0.02
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
    
    def CalculateUpri(self, z_scores = None):
        # Equation 15
        if z_scores is None:
        # Fallback to illustrative specification Z-scores
            protective_list = [0.42, 1.20, 0.40, 0.33]  # sum = 2.35
            adverse_list = [0.46, 0.83, 0.58, 0.99]      # sum = 2.86
        else:
            # Map protective Z-scores from Step 3
            protective_list = [
                z_scores.get("NDVI", 0.42),
                z_scores.get("Walkability", 1.20),
                0.40,  # Social
                0.33   # Dwell
            ]
            # Map adverse Z-scores from Step 3
            adverse_list = [
                z_scores.get("f_PM", 0.46),
                z_scores.get("NoiseNight", 0.83),
                z_scores.get("f_H", 0.58),
                z_scores.get("f_NH", 0.99)
            ]

        sum_p = sum(protective_list)
        sum_h = sum(abs(v) for v in adverse_list)

        if sum_h == 0:
            raise ValueError("Stressor sum cannot be zero.")

        return sum_p / sum_h