
class UrbanVitalSigns:
    def __init__(self, root):     
        self.root = root

    def CalculateNex(self, z_ndvi, other_z_values=None):
        # Equation 7
        if other_z_values is None:
            # Default remaining 6 inputs to +0.20 each
            other_z_values = [0.20] * 6

        if len(other_z_values) != 6:
            raise ValueError("other_z_values must contain exactly 6 elements.")

        total_sum = z_ndvi + sum(other_z_values)
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

    