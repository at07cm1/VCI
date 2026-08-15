import math

class SpecificationRules:
    def __init__(self, root):     
        self.root = root

    def calculate_z_score(self, val, mu, sigma):
        # Equation 1
        if sigma == 0:
            raise ValueError("Standard deviation (sigma) cannot be zero.")
        return (val - mu) / sigma

    def calculate_f_pm(self, x, x_ref):
        # Equation 2
        if x < 0:
            raise ValueError("PM2.5 concentration (x) cannot be negative.")
            
        numerator = math.log(x + 1)
        denominator = math.log(x_ref + 1)
        
        return numerator / denominator

    def calculate_f_h(self, T, T_MMT, s_T):
        # Equation 3
        if s_T == 0:
            raise ValueError("Scale parameter (s_T) cannot be zero.")
            
        return ((T - T_MMT) / s_T) ** 2

    def calculate_f_nh(self, T, T_thr):
        # Equation 4
        # max(0, T - T_thr) ensures the value stays 0 when below the threshold
        diff = max(0.0, T - T_thr)
        
        return diff ** 1.5

    def apply_orientation(self, value, is_cmx=False):
        # Equation 5
        s_k = -1.0 if is_cmx else 1.0
        return s_k * value

    def normalize_vital_sign(self, v_oriented, alpha=-2.0, beta=2.0):
        # Equation 6
        if beta == alpha:
            raise ValueError("Upper bound (beta) and lower bound (alpha) cannot be equal.")
            
        normalized = (v_oriented - alpha) / (beta - alpha)
        
        # Clamp bounds strictly within [0, 1] interval
        return max(0.0, min(1.0, normalized))