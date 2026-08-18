
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

    