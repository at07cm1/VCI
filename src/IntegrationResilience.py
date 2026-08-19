
class IntegrationResilience:
    def __init__(self, root):     
            self.root = root
            self.default_allocations = {
                "NDVI": {"NEX": 0.40, "SRB": 0.30, "CEV": 0.30},
                "f_PM": {"CMX": 0.50, "SRB": 0.50},
                "NoiseNight": {"SRB": 0.50, "CMX": 0.50}
        }

    def CalculateVci(
        self, 
        normalized_domains, 
        alpha_k=1/6, 
        gamma=0.10, 
        interaction_sum=1.35, 
        centering_const=0.50
    ):
        # Equation 13
        # 1. Weighted sum of domains
        weighted_sum = alpha_k * sum(normalized_domains.values())
        
        # 2. Interaction sum
        interaction_term = gamma * interaction_sum
        
        # 3. Raw VCI
        vci_raw = weighted_sum + interaction_term
        
        # 4. Centering to [-1, +1] manuscript scale
        vci_centered = (vci_raw - centering_const) * 2.0
        
        return vci_raw, vci_centered

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