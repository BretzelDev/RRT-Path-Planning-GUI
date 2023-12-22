import numpy as np

class Node:
    def __init__(self, z, world, parent = None):
        self.z = z ## State vector
        self.children = [] ## Node children list
        self.world = world ## Obstacle set (boolean array)
        self.parent = parent ## Parent node


    def insert_node(self, node):
        if node not in self.children:
            self.children.append(node)

    def assign_parent(self, parent):
            assert parent != self
            self.parent = parent

    def is_obstacle_free(self, potential_parent):
        pass
    
    def get_pos(self):
        return self.z[:2]
    
    def __str__(self):
        return f"({self.z[0]}, {self.z[1]})"
    
    def print(self):
        string =  str(self) + " --> "+ ("==".join([child.print() for child in self.children]))
        return string

         
    

class Tree(Node):
    def __init__(self, z, world):
        super().__init__(z, world)

    def unpack_tree(self):
        pass



class RandomStateGenerator:
    def __init__(self, limits):
        self.limits = np.array(limits)
        self.n = len(self.limits)

        self.check_limits()

    def __call__(self):
        generated_value = np.random.random(self.n)
        generated_value = generated_value * (self.limits[:,1] - self.limits[:,0]) + self.limits[:,0]
        return generated_value
    
    def check_limits(self):
        assert (self.limits[:,1] > self.limits[:,0]).all()


class RRTStar:
    def __init__(self, world, limits, z_init=None):
        self.limits = limits
        self.world = world
        self.rsg = RandomStateGenerator(limits)

        self.root = Tree(z_init, self.world)

    def init_tree(self, z_init):
        self.root = Tree(z_init, self.world)


        


if __name__ == "__main__":
    limits = [[0,10],
              [0,10]]
    rsg = RandomStateGenerator(limits)

    print("## Test de génération d'états aléatoires")
    testvalue = rsg()

    walls = np.random.random((11, 11)).astype(bool)

    root = Tree(testvalue, walls)

    rand_z = rsg()

    root.insert_node(Node(rand_z, walls))

    rand_z = rsg()
    root.insert_node(Node(rand_z, walls))


    print(root.children)

    print(root.print())

    

