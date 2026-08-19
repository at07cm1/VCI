
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
    
    def CalculateUpri(self, sum_protective=2.10, sum_stressors=2.55):
        # Equation 15
        if sum_stressors == 0:
            raise ValueError("Stressor sum cannot be zero.")
            
        return sum_protective / abs(sum_stressors)