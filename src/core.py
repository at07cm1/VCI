
class VciCalculator:
    def __init__(self, root):
        self.root = root    
        self.root.title("VCI Calculator")
        self.root.state('zoomed')

        # ----- UI Elements ------