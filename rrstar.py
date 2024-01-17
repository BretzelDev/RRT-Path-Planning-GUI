import numpy as np
from numba import jit, float64, int32, njit
import numba as nb
from time import time
from math import sqrt



@njit
def sample(limits):
    a, b = np.random.random(2)
    return np.array([limits[0][0] + (limits[0][1] - limits[0][0]) * a, limits[1][0] + (limits[1][1] - limits[1][0]) * b])

@njit
def neighborhood(z, tree: np.ndarray, world: np.ndarray):
    l = np.inf
    distances = []
    indices = []
    N = tree.shape[0]
    for i in range(N):
        distance = sqrt((tree[i, 2] - z[1])**2 + (tree[i,3] - z[1])**2)
        if distance <= l:
            distances.append(distance)
            indices.append(i)

    return distances

@njit
def rrtstar(iterations: int, limits, world: np.ndarray, robot: tuple, goal: tuple):
    tree = np.zeros((iterations, len(limits[0])+2), dtype=np.float32)
    tree[0, 2:] = robot[::-1]

    for iteration in range(iterations-1):
        ## Sample
        # a, b = np.random.random(2)
        # z_new = np.array([limits[0][0] + (limits[0][1] - limits[0][0]) * a, limits[1][0] + (limits[1][1] - limits[1][0]) * b])
        
        ## Neighborhood computation
        l = np.inf
        distances = []
        indices = []
        res_seg = 200
        T = np.linspace(0,1, res_seg)
        while not indices:
            ## new Sample
            a, b = np.random.random(2)
            z_new = np.array([limits[0][0] + (limits[0][1] - limits[0][0]) * a, limits[1][0] + (limits[1][1] - limits[1][0]) * b])
            dist_min = np.inf
            ind_min = 0
            for i in range(iteration+1):
                distance = sqrt((tree[i, 2] - z_new[0])**2 + (tree[i,3] - z_new[1])**2)
                if distance <= l:
                    valid_link = True
                    for t in T:
                        # pos = np.asarray(t * tree[i,2:4] + (1-t) * z_new, dtype=int32)
                        posx = int32(t*tree[i,2]+(1-t)*z_new[0])
                        posy = int32(t*tree[i,3]+(1-t)*z_new[1])

                        if world[posx, posy]:
                            valid_link = False
                            break
                    if valid_link:
                        distances.append(distance)
                        indices.append(i)
                        if distance <= dist_min:
                            dist_min = distance
                            ind_min = i
        ## End of neighborhood computation
                            
        
        nb = len(indices)
        cost_min = np.inf
        ind_min = 0
        for i in range(nb):
            potential_cost = distances[i] + tree[indices[i], 1]
            if potential_cost < cost_min:
                cost_min = potential_cost
                ind_min = indices[i]
        tree[iteration+1] = np.array([ind_min, cost_min] + list(z_new))
        # print(iteration + 1)
        
        for i in range(nb):
            if indices[i] != ind_min and distances[i] + cost_min < tree[indices[i], 1]:
                tree[indices[i], 1] = distances[i] + cost_min
                tree[indices[i], 0] = iteration + 1
            # else:
            #     print("test")

            
        # cost_new = dist_min + tree[ind_min, 1]
        # nb = len(indices)
        # for i in range(nb):
        #     potential_new_cost = cost_new + distances[i]
        #     if potential_new_cost < tree[indices[i], 1]:
        #         tree[indices[i],1] = potential_new_cost
        #         tree[indices[i],0] = iteration + 1
        # tree[iteration+1] = np.array([ind_min, cost_new] + list(z_new))

    
    return tree


if __name__ == "__main__":
    N = 100000
    limits = nb.typed.List([[0, 300], [0, 500]])
    world = np.random.randint(0,2, size=(300, 600), dtype=bool) * 0
    robot = (123, 456)
    goal = (0, 0)
    iterations = 10000

    start = time()
    test = rrtstar(N, limits, world, robot, goal)
    length = time() - start
    print("####### TEST FUNCTION #######")
    print(test)
    print(f"Result obtained in {length:.2}")

    start = time()
    test = rrtstar(N, limits, world, robot, goal)
    length = time() - start
    print("####### TEST FUNCTION #######")
    print(test)
    print(f"Result obtained in {length:.2}")


    # array = np.random.random((N, 4))
    # start = time()
    # test = neighborhood(robot, array, world) #np.zeros((N, len(limits[0])), dtype=bool)
    # length = time() - start
    # print("####### TEST NEIGHBORHOOD #######")
    # print(test)
    # print(f"Result obtained in {length:.2}")




    # array = np.random.random((N, 4))
    # start = time()
    # test = distances = np.sum((array[:,2:4] - robot)**2, axis=1)
    # length = time() - start


    # print("####### TEST NEIGHBORHOOD #######")
    # print(test)
    # print(f"Result obtained in {length:.2}")



