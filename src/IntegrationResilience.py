
class IntegrationResilience:
    def __init__(self, root):     
            self.root = root

    def calculate_vci(
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