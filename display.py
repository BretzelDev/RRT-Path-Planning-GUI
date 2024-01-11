import numpy as np
import matplotlib
from RRTstar import unpack_tree_array, unpack_tree_array_parallel


rgb = {}
for name, hex in matplotlib.colors.cnames.items():
    rgb[name] = np.array(matplotlib.colors.to_rgb(hex)) * 255


default_colors = {
    "background": "white",
    "wall": "black",
    "robot": "orange",
    "goal": "red",
    "tree": "green",
    "path": "red"
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
        self.tree_color = rgb[colorset["tree"]]
        self.path_color = rgb[colorset["path"]]


        ## Sizes
        self.robot_size = 30
        self.goal_size = 30

        self.tree_mask = None
        self.path_mask  = None



    def __call__(self, walls=None, robot=None, goal=None, tree=None, new_tree=False, path=None, new_path=False):
        img = np.zeros(self.shape, dtype=np.uint8)

        img[...,:] = self.background_color ## Background drawing
        if walls is not None:
            img[walls] = self.wall_color ## Wall drawing

        if robot is not None:
            img[robot[1]-self.robot_size//2:robot[1]+self.robot_size//2+1, robot[0]-self.robot_size//2:robot[0]+self.robot_size//2+1] = self.robot_color
        
        if goal is not None:
            img[goal[1]-self.goal_size//2:goal[1]+self.goal_size//2+1, goal[0]-self.goal_size//2:goal[0]+self.goal_size//2+1] = self.goal_color

        if tree is not None:
            if new_tree:
                self.tree_mask = self.draw_tree(tree)
            img[self.tree_mask[:,0], self.tree_mask[:,1]] = self.tree_color

        if path is not None:
            if new_path:
                self.path_mask = self.draw_path(path)
            img[self.path_mask[:,0], self.path_mask[:,1]] = self.path_color
                

        return img
    
    def draw_tree(self, root, res_seg=100):
        tree = unpack_tree_array(root)#np.array(root.draw_edges())
        T = np.linspace(0,1, res_seg).reshape((1,-1,1))
        inter = T * tree[:,0,:].reshape((-1, 1, 2)) + (1-T) * tree[:,1,:].reshape((-1, 1, 2))
        inter = inter.reshape((-1, 2))
        inter = np.int32(inter)
        return inter

    def draw_path(self, path, res_seg=100):
        T = np.linspace(0,1, res_seg).reshape((1,-1,1))
        inter = T * path[:,0,:].reshape((-1, 1, 2)) + (1-T) * path[:,1,:].reshape((-1, 1, 2))
        inter = inter.reshape((-1, 2))
        inter = np.int32(inter)
        return inter

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
        


    