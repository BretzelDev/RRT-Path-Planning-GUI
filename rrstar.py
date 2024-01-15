import numpy as np
from numba import jit, float64, int32

@jit(nopython=True)
def euclidean_distance(p1, p2):
    p1_float64 = np.array([p1[0], p1[1]], dtype=np.float64)
    p2_float64 = np.array([p2[0], p2[1]], dtype=np.float64)
    return np.linalg.norm(p1_float64 - p2_float64)

@jit(nopython=True)
def nearest_neighbor(tree, target_point):
    min_distance = np.inf
    nearest_node = None

    for node in tree:
        distance = euclidean_distance(node, target_point)
        if distance < min_distance:
            min_distance = distance
            nearest_node = node

    return nearest_node

@jit(nopython=True)
def steer(from_point, to_point, max_distance):
    if to_point is None:
        return from_point  # If no specific target, stay at the current point

    to_point_array = np.asarray(to_point)
    from_point_array = np.asarray(from_point)
    direction = to_point_array - from_point_array
    distance = np.linalg.norm(direction)
    
    if distance <= max_distance:
        return to_point_array  # If the target is within max_distance, go directly to it
    else:
        normalized_direction = direction / distance
        return (from_point + max_distance) * normalized_direction

@jit(nopython=True)
def is_collision_free(world, p1, p2):
    # Check if the line segment between p1 and p2 is collision-free
    step_size = 0.1
    t = np.arange(0, 1, step_size)
    path = p1 + t[:, None] * (p2 - p1)
    
    for point in path:
        x, y = point.astype(int)
        if not (0 <= x < world.shape[0] and 0 <= y < world.shape[1] and not world[x, y]):
            return False
    
    return True

@jit(nopython=True)
def rewire(tree, new_point, max_distance):
    for i in range(len(tree)):
        node = tree[i]
        if euclidean_distance(new_point, node) < max_distance:
            if is_collision_free(tree, new_point, node):
                tree[i] = new_point

@jit(nopython=True)
def rrt_star(world, start, goal, max_iterations=1000, max_distance=10.0):
    tree = [start]

    for _ in range(max_iterations):
        random_point = np.random.rand(2) * np.array(world.shape)
        nearest_node = nearest_neighbor(tree, random_point)
        new_point = steer(nearest_node, random_point, max_distance)

        if is_collision_free(world, nearest_node, new_point):
            near_nodes = [node for node in tree if euclidean_distance(node, new_point) < max_distance]
            cost = np.argmin([tree.index(node) + euclidean_distance(node, new_point) for node in near_nodes])

            tree.append(new_point)

            for node in near_nodes:
                if tree.index(node) + euclidean_distance(node, new_point) < tree.index(new_point):
                    if is_collision_free(world, node, new_point):
                        tree[-1] = node

            if cost < len(tree):
                tree[-1] = near_nodes[cost]

                rewire(tree, new_point, max_distance)

    return tree
