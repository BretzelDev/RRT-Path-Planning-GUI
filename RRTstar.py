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
    
    def nearest(self, z):
        if self.children:
            return min([[self, self.distance(z)]] + [child.nearest(z) for child in self.children], key = lambda x: x[1])
        return [self, self.distance(z)]
    
    def near(self, z, n, d=2):
        gamma = 10
        l = gamma * (np.log(n)/n)**d
        print("l = ", l)
        result = [self] * int(self.distance(z) <= l)
        for child in self.children:
            result += child.near(z, n, d)
        return result
        # return [self] * int(self.distance(z) <= l) + [child.near(z, n, d) for child in self.children] 


    def distance(self, z):
        return np.sum((self.z[:2]-z[:2])**2)
    
    def draw_edges(self, depth=0):
        edges = []
        for child in self.children:
            edges.append([self.z[:2], child.z[:2]])
            edges += child.draw_edges(depth+1)
        return edges

         
    
def generate_random_tree(limits, N=100):
    walls = np.random.random((11, 11)).astype(bool)
    rsg = RandomStateGenerator(limits)
    root = Tree(rsg(), walls)
    for i in range(N-1):
        z_new = rsg()
        nearest = root.nearest(z_new)[0]
        nearest.insert_node(Node(z_new, walls, nearest))

    return root



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


    rand_z = rsg()
    root.insert_node(Node(rand_z, walls))


    rand_z = rsg()
    root.insert_node(Node(rand_z, walls))

    rand_z = rsg()

    
    nearest = root.nearest(rand_z)
    print("nearest : ", nearest)


    near  = root.near(rand_z, 4, 2)
    print("near : ", near)
    # print(nearest[0])
    # print(nearest[1])

    # print(root.children)

    limits = [[0,1200],
              [0,800]]
    root = generate_random_tree(limits)

    draw = np.array(root.draw_edges())
    T = np.linspace(0,1, 100).reshape((1,-1,1))

    inter = T * draw[:,0,:].reshape((-1, 1, 2)) + (1-T) * draw[:,1,:].reshape((-1, 1, 2))
    inter = inter.reshape((-1, 2))
    inter = np.unique(np.int32(inter), axis=0)


    print(inter.shape)



    print(draw.shape)

    print(root.print())

    

