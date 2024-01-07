import numpy as np

def annd(graph, mode="all", len_deg_seq=None):
    if mode=="all":
        new_graph = graph.as_undirected()
    else:
        new_graph = graph
    annd_array = np.zeros(len(new_graph.vs))
    annd_k = np.zeros(len_deg_seq) if len_deg_seq else np.zeros(max(new_graph.degree(mode=mode)))
    degree_hist = np.zeros(len_deg_seq) if len_deg_seq else np.zeros(max(new_graph.degree(mode=mode)))
    for i in range(len(new_graph.vs)):
        vertex = new_graph.vs[i]
        degree = vertex.degree(mode=mode, loops=False)
        neighbors = vertex.neighbors(mode=mode)
        annd_array[i] = np.mean([neighbor.degree(mode=mode, loops=False) for neighbor in neighbors if neighbor != vertex])
        if degree>0:
            degree_hist[degree-1] += 1
            annd_k[degree-1] += annd_array[i]
    annd_k = annd_k/degree_hist
    return annd_array, annd_k

# def anns(graph, mode):
#     new_graph = graph
#     anns_array = np.zeros(len(new_graph.vs))
#     for i in range(len(new_graph.vs)):
#         vertex = new_graph.vs[i]
#         neighbors = vertex.neighbors(mode=mode)
#         num_neighbors = 0
#         for neighbor in neighbors:
#             if neighbor == vertex:
#                 continue
#             second_neighbors = neighbor.neighbors(mode=mode)
#             strength = 0
#             for second_neighbor in second_neighbors:
#                 if second_neighbor == neighbor:
#                     continue
#                 strength += graph.es[graph.get_eid(neighbor, second_neighbor)]["weight"] if mode=="out" else graph.es[graph.get_eid(second_neighbor, neighbor)]["weight"]
#             anns_array[i] += strength
#             num_neighbors += 1
#         anns_array[i] = anns_array[i]/num_neighbors
#     return anns_array

def anns(graph, mode):
    adj_matrix = np.array(graph.get_adjacency().data)
    np.fill_diagonal(adj_matrix, 0)
    w_adj_matrix = np.array(graph.get_adjacency(attribute='weight').data)
    np.fill_diagonal(w_adj_matrix, 0)
    if mode=="out":
        multiplied = np.matmul(adj_matrix, w_adj_matrix)
        result = np.sum(multiplied, axis=1)/np.sum(adj_matrix, axis=1)
    if mode=="in":
        multiplied = np.matmul(w_adj_matrix, adj_matrix)
        result = np.sum(multiplied, axis=0)/np.sum(adj_matrix, axis=0)
    return result
        

"""
def clustering_coeff_old(graph, len_deg_seq=None):
    new_graph = graph.as_undirected()
    clustering_coeff_array = graph.transitivity_local_undirected()
    clustering_coeff_k = np.zeros(len_deg_seq) if len_deg_seq else np.zeros(max(new_graph.degree()))
    degree_hist = np.zeros(len_deg_seq) if len_deg_seq else np.zeros(max(new_graph.degree()))
    for i in range(len(new_graph.vs)):
        degree = new_graph.vs[i].degree()
        if degree>0:
            clustering_coeff_k[degree-1] += clustering_coeff_array[i]
            degree_hist[degree-1] += 1
    clustering_coeff_k = clustering_coeff_k/degree_hist
    return clustering_coeff_array, clustering_coeff_k
"""

def clustering_coeff(graph, len_deg_seq=None):
    new_graph = graph.as_undirected()
    clustering_coeff_array = np.zeros(graph.vcount())
    clustering_coeff_k = np.zeros(len_deg_seq) if len_deg_seq else np.zeros(max(new_graph.degree()))
    degree_hist = np.zeros(len_deg_seq) if len_deg_seq else np.zeros(max(new_graph.degree()))
    for i in range(graph.vcount()):
        vertex = new_graph.vs[i]
        degree = vertex.degree(loops=False)
        neighbors = vertex.neighbors()
        num_wedges = 0
        for neighbor1 in neighbors:
            if neighbor1 == vertex:
                continue
            for neighbor2 in neighbors:
                if neighbor2 == vertex or neighbor2 == neighbor1:
                    continue
                num_wedges += 1
                if graph.are_connected(neighbor1, neighbor2):
                    clustering_coeff_array[i] += 1
        clustering_coeff_array[i] = clustering_coeff_array[i]/num_wedges
        clustering_coeff_k[degree-1] += clustering_coeff_array[i]
        degree_hist[degree-1] += 1
    clustering_coeff_k = clustering_coeff_k/degree_hist
    return clustering_coeff_array, clustering_coeff_k

def clustering_coeff_matrix(graph):
    new_graph = graph.as_undirected()
    adj_matrix = np.array(new_graph.get_adjacency().data)
    np.fill_diagonal(adj_matrix, 0)
    


def weighted_clustering_coeff(graph):
    w_cl_coeff_array = np.zeros(graph.vcount())
    for i in range(graph.vcount()):
        vertex = graph.vs[i]
        neighbors_out = vertex.neighbors(mode="out")
        neighbors_in = vertex.neighbors(mode="in")
        num_wedges = 0
        for neighbor_out in neighbors_out:
            if neighbor_out == vertex:
                continue
            for neighbor_in in neighbors_in:
                if neighbor_out != neighbor_in and neighbor_in != vertex:
                    num_wedges += 1
                    if graph.are_connected(neighbor_out, neighbor_in):
                        w_ij = graph.es[graph.get_eid(vertex, neighbor_out)]["weight"]
                        w_jk = graph.es[graph.get_eid(neighbor_out, neighbor_in)]["weight"]
                        w_ki = graph.es[graph.get_eid(neighbor_in, vertex)]["weight"]
                        w_cl_coeff_array[i] += (w_ij*w_jk*w_ki)**(1/3)
        w_cl_coeff_array[i] = w_cl_coeff_array[i]/num_wedges
    return w_cl_coeff_array