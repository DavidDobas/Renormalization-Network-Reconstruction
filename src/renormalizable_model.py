import igraph as ig
import numpy as np

def assign_weight(x_i, y_j, p_ij, W):
    return x_i*y_j/(p_ij*W)

def check_weighted_consistency(strenghts):
    x_i_array, y_i_array = zip(*strenghts)
    if np.sum(x_i_array) != np.sum(y_i_array):
        raise Exception("Inconsistent weights")

def create_RM_graph(strenghts, z, weighted=False):
    if weighted:
        check_weighted_consistency(strenghts)
        W = np.sum(list(zip(*strenghts))[0])
    n = len(strenghts)
    graph = ig.Graph(n, edges=[], directed=True)
    edges_to_add = []
    weights_to_add = []
    random_numbers = np.random.random_sample([n,n])
    for i in range(n):
        for j in range(n):
            x_i = strenghts[i][0]
            y_j = strenghts[j][1]
            p_ij = 1 - np.exp(-z*x_i*y_j) if z < np.infty else 1
            if random_numbers[i][j] < p_ij:
                edges_to_add.append((i,j))
                if weighted:
                    weights_to_add.append(assign_weight(x_i, y_j, p_ij, W))
    graph.add_edges(edges_to_add)
    if weighted:
        graph.es["weight"] = weights_to_add
    return graph

def generate_RM_ensemble(n, strenghts, z, weighted=False):
    return [create_RM_graph(strenghts, z, weighted) for i in range(n)]

# Assure that sum of outcoming strenghts is the same as sum of incoming strenghts
def make_strenghts_consistent(strenghts):
    new_strenghts = np.copy(strenghts)
    x_i_arr, y_i_arr = zip(*new_strenghts)
    x_sum = np.sum(x_i_arr)
    y_sum = np.sum(y_i_arr)
    new_strenghts[-1,1] = new_strenghts[-1,1] + x_sum - y_sum
    return new_strenghts