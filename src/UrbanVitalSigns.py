
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

    