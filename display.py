import numpy as np
import matplotlib

rgb = {}
for name, hex in matplotlib.colors.cnames.items():
    rgb[name] = np.array(matplotlib.colors.to_rgb(hex)) * 255


default_colors = {
    "background": "white",
    "wall": "black",
    "robot": "orange",
    "goal": "red"
}

class Display:
    def __init__(self, height, width, colorset=default_colors):
        ## Dimensions
        self.height, self.width = height, width
        self.shape = (self.height, self.width, 3)

        ## Colors
        self.background_color = rgb[colorset["background"]]
        self.wall_color = rgb[colorset["wall"]]
        self.robot_color = rgb[colorset["robot"]]
        self.goal_color = rgb[colorset["goal"]]

        ## Sizes
        self.robot_size = 30
        self.goal_size = 30


    def __call__(self, walls=None, robot=None, goal=None):
        img = np.zeros(self.shape, dtype=np.uint8)

        img[...,:] = self.background_color ## Background drawing
        if walls is not None:
            img[walls] = self.wall_color ## Wall drawing

        if robot is not None:
            img[robot[1]-self.robot_size//2:robot[1]+self.robot_size//2+1, robot[0]-self.robot_size//2:robot[0]+self.robot_size//2+1] = self.robot_color
        
        if goal is not None:
            img[goal[1]-self.goal_size//2:goal[1]+self.goal_size//2+1, goal[0]-self.goal_size//2:goal[0]+self.goal_size//2+1] = self.goal_color

        return img
    
    def get_background_color(self):
        return self.background_color


    def switch_background_color(self, color):
        if type(color) == str:
            self.background_color = rgb[color]
        else:
            self.background_color = color

    def switch_wall_color(self, color):
        if type(color) == str:
            self.wall_color = rgb[color]
        else:
            self.wall_color = color

    def switch_robot_color(self, color):
        if type(color) == str:
            self.robot_color = rgb[color]
        else:
            self.robot_color = color

    def switch_goal_color(self, color):
        if type(color) == str:
            self.goal_color = rgb[color]
        else:
            self.goal_color = color
        


    