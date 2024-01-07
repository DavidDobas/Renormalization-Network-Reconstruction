import igraph as ig
import numpy as np
from src import renormalizable_model

def coarse_grain_strengths(strengths, group_sequence):
    new_strengths = np.zeros((len(group_sequence), 2))
    for i in range(len(group_sequence)):
        new_strengths[i] = np.sum([strengths[j] for j in group_sequence[i]], axis=0)
    return new_strengths

def coarse_grain_weighted_graph(graph, group_sequence):
    new_graph = renormalizable_model.Graph_with_properties(len(group_sequence), edges=[], directed=True)
    edges_to_add = []
    weights_to_add = []
    for i in range(len(group_sequence)):
        for j in range(len(group_sequence)):
            connected = False
            total_weight = 0
            for k in group_sequence[i]:
                for l in group_sequence[j]:
                    #print(k, l)
                    if graph.are_connected(k, l):
                        #print(k, l, "connected, adding weight", graph.es[graph.get_eid(k,l)]["weight"])
                        connected = True
                        total_weight += graph.es[graph.get_eid(k,l)]["weight"]
            if connected:
                edges_to_add.append((i,j))
                weights_to_add.append(total_weight)
    new_graph.add_edges(edges_to_add)
    new_graph.es["weight"] = weights_to_add
    return new_graph

def divide_graph_equally(graph, num_groups):
    return np.array_split(graph.vs.indices, num_groups)

def merge_n_group(graph, n):
    return [graph.vs.indices[:n], *[[index] for index in graph.vs.indices[n:]]]