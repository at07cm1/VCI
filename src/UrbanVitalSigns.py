
class UrbanVitalSigns:
    def __init__(self, root):     
        self.root = root

    def CalculateNex(self, z_scores):
        # Equation 7
        nex_keys = [
            "NDVI", "GVI", "AccessGreen", 
            "Canopy", "Blue", "Micro", "Sidewalk"
        ]
        
        # Sum the 7 NEX Z-scores
        total_sum = sum(z_scores[key] for key in nex_keys)
        
        return total_sum / 7.0

    def CalculateSev(self, sev_z_values=None):
        # Equation 8
        if sev_z_values is None:
            # Default illustrative Z-values matching Equation 8
            sev_z_values = [0.30, 0.50, 0.40, 0.20, 0.60, 0.10, 0.70]

        if len(sev_z_values) != 7:
            raise ValueError("sev_z_values must contain exactly 7 Z-scores.")

        # Equal weighting w_i = 1/7
        return sum(sev_z_values) / 7.0
    
    def CalculateNte(
        self, 
        z_noise, 
        z_nh, 
        z_daylight=0.30, 
        z_light_night=0.60, 
        z_humid_night=0.40, 
        w=0.25
    ):
        # Equation 9
        positive_part = w * z_daylight
        negative_part = w * (z_light_night + z_noise + z_nh + z_humid_night)
        
        return positive_part - negative_part

    def CalculateCmx(
        self, 
        z_f_pm, 
        z_f_h, 
        z_noise=0.50, 
        z_inactivity=0.30, 
        z_commute=0.40, 
        z_housing=0.60, 
        beta=1/6
    ):
        # Equation 10
        cmx_sum = z_f_pm + z_noise + z_f_h + z_inactivity + z_commute + z_housing
        return beta * cmx_sum

    def CalculateCev(
        self,
        z_sum,
        n_inputs=9,
        c=0.72,
        c_opt=0.55,
        s_c=0.20,
        w10=0.30
    ):
        # Equation 11
        linear_part = z_sum / n_inputs
        penalty = w10 * (((c - c_opt) / s_c) ** 2)
        
        return linear_part - penalty

    def calculate_srb(self, protective_list=None, adverse_list=None):
        # Equation 12
        if protective_list is None:
            # Default illustrative protective values: greenness, walkability, social, dwell
            protective_list = [0.42, 1.20, 0.40, 0.33]

        if adverse_list is None:
            # Default illustrative adverse values: PM2.5, noise, heat
            adverse_list = [0.46, 0.83, 0.58]

        sum_p = sum(protective_list)
        sum_h = sum(adverse_list)
        
        sum_abs_p = sum(abs(p) for p in protective_list)
        sum_abs_h = sum(abs(h) for h in adverse_list)

        denominator = sum_abs_p + sum_abs_h
        if denominator == 0:
            return 0.0

        return (sum_p - sum_h) / denominator