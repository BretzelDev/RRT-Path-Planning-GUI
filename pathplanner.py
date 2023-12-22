import numpy as np
from display import Display

class PathPlanner:
    def __init__(self, interface, display, height, width, method=None):
        self.interface = interface
        self.display = display

        self.walls = np.zeros((self.canvas_height, self.canvas_width), dtype=bool)
        self.robot = None
        self.goal = None


    