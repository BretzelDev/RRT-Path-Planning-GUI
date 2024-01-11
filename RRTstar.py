import numpy as np
import threading
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

def generate_random_tree_array(limits, N=100):
    rsg = RandomStateGenerator(limits)
    root = TreeArray(limits)
    for i in range(N-1):
        z_new = rsg()
        nearest = root.nearest(z_new)
        root.append_state(root.create_row(nearest, z_new))

    return root
        
def unpack_tree_array(root):
    N, D = root.array.shape

    print("## " ,N, D)
    
    links = np.zeros((N-1, 2, D-2))
    for i in range(1, N):
        links[i-1, 0] = root.array[i,2:]
        links[i-1,1] = root.array[int(root.array[i,0]), 2:]

    return links

def unpack_tree_array_parallel(root):
    N, D = root.array.shape

    # Split the range into two halves
    midpoint = N // 2

    # Shared data structure to store the results
    links = np.zeros((N-1, 2, D-1))

    # Helper function to process each half
    def process_half(start, end):
        for i in range(start, end):
            links[i-1, 0] = root.array[i, 1:]
            links[i-1, 1] = root.array[int(root.array[i, 0]), 1:]

    # Create two threads, each responsible for one half of the array
    thread1 = threading.Thread(target=process_half, args=(1, N//3))
    thread2 = threading.Thread(target=process_half, args=(N//3, 2*N//3))
    thread3 = threading.Thread(target=process_half, args=(2*N//3, N))

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()
    thread2.join()

    return links

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


class TreeArray:
    def __init__(self, z_init):
        # self.limits = limits
        # self.rsg = RandomStateGenerator(limits)
        self.array = np.array([self.create_row(0, z_init, cost=0)])
        
    def nearest(self, z):
        distances = np.sum((self.array[:,2:4] - z)**2, axis=1)
        index = np.argmin(distances)
        return index, distances[index]
    
    def neighborhood(self, z, d=2):
        gamma = 10
        n = self.array.shape[0]
        l = gamma * (np.log(n)/n)**d
        l = np.inf
        distances = np.sum((self.array[:,2:4] - z)**2, axis=1)
        z_nearest_index = np.argmin(distances)
        z_nearest_distance = distances[z_nearest_index]
        index = np.argwhere(distances <= l)
        return index, distances[index], z_nearest_index, z_nearest_distance

    def append_state(self, row):
        self.array = np.vstack((self.array, row))

    def create_row(self, parent, z, cost=np.inf):
        return np.hstack(([parent], [cost], z))
    
    def change_parent(self, nodeIndex, newParentIndex):
        self.array[nodeIndex,0] = newParentIndex

    def add_node(self, parent, z, cost=np.inf):
        new_row = self.create_row(parent, z, cost)
        self.append_state(new_row)


class RRTStar:
    def __init__(self, world, limits, z_init=None):
        self.limits = limits
        self.world = world
        self.rsg = RandomStateGenerator(limits)
        if z_init is None:
            z_init = self.rsg()
        else:
            z_init = z_init[::-1]
        self.root = TreeArray(z_init)

    def init_tree(self, z_init):
        self.root = TreeArray(z_init, self.world)


    def __call__(self, iterations = 1000):
        for i in range(iterations):
            z_new = self.rsg() 
            while True:
                if not is_in_obstacle(z_new, self.world): ## We generate a random state until we obtain one free of any obstacle
                    break
                z_new = self.rsg()

            # z_nearest_index, distance2nearest = self.root.nearest(z_new)
            z_neighbours_index, z_neighbor_distances, z_nearest_index, distance2nearest = self.root.neighborhood(z_new)
            cost_new = distance2nearest + self.root.array[z_nearest_index, 1]
            neighbors_costs = self.root.array[z_neighbours_index,1]
            # best_parent_index = np.argmin(neighbors_costs)
            # best_parent_cost = z_neighbor_distances[best_parent_index]
            # best_parent = z_neighbours_index[best_parent_index]

            potential_new_costs = cost_new + z_neighbor_distances
            mask_neighbors = potential_new_costs < neighbors_costs
            # index_neighbors_to_change = np.argwhere(mask_neighbors)
            if mask_neighbors.any():
                self.root.array[z_neighbours_index[mask_neighbors], 1] = potential_new_costs[mask_neighbors]
                self.root.array[z_neighbours_index[mask_neighbors], 0] = i+1
                # print(self.root.array.shape[0])

            self.root.add_node(z_nearest_index, z_new, cost=cost_new)
            
            

                


def is_in_obstacle(z, world): #TODO function that determines if the node is inside an obstacle or not
    val = world[int(z[0]), int(z[1])]
    return val

def euclidean_distance(z1, z2):
    return


    # Rad = r
    # G(V,E) //Graph containing edges and vertices
    # For itr in range(0…n)
    #     Xnew = RandomPosition()
    #     If Obstacle(Xnew) == True, try again
    #     Xnearest = Nearest(G(V,E),Xnew)
    #     Cost(Xnew) = Distance(Xnew,Xnearest)
    #     Xbest,Xneighbors = findNeighbors(G(V,E),Xnew,Rad)
    #     Link = Chain(Xnew,Xbest)
    #     For x’ in Xneighbors
    #         If Cost(Xnew) + Distance(Xnew,x’) < Cost(x’)
    #             Cost(x’) = Cost(Xnew)+Distance(Xnew,x’)
    #             Parent(x’) = Xnew
    #             G += {Xnew,x’}
    #     G += Link 
    # Return G




    
    
    

        


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


    print("##### draw")
    print(draw.shape)

    tree = TreeArray(limits)
    
    z = rsg()
    print(tree.nearest(z))

    # print(root.print())
    print(tree.array)

    print(" TEST ARRAY")

    tree = generate_random_tree_array(limits)

    edges = unpack_tree_array(tree)
    print(edges)
    print(edges.shape)


    

