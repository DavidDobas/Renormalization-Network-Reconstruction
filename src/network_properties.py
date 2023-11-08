import numpy as np

def annd(graph, mode="all"):
    if mode=="all":
        new_graph = graph.as_undirected()
    else:
        new_graph = graph
    annd_array = np.zeros(len(new_graph.vs))
    annd_k = np.zeros(max(new_graph.degree(mode=mode)))
    degree_hist = np.zeros(max(new_graph.degree(mode=mode)))
    for i in range(len(new_graph.vs)):
        vertex = new_graph.vs[i]
        degree = vertex.degree(mode=mode)
        neighbors = vertex.neighbors(mode=mode)
        annd_array[i] = np.mean([neighbor.degree(mode=mode) for neighbor in neighbors])
        if degree>0:
            degree_hist[degree-1] += 1
            annd_k[degree-1] += annd_array[i]
    annd_k = annd_k/degree_hist
    return annd_array, annd_k

def clustering_coeff(graph):
    new_graph = graph.as_undirected()
    clustering_coeff_array = graph.transitivity_local_undirected()
    clustering_coeff_k = np.zeros(max(new_graph.degree()))
    degree_hist = np.zeros(max(new_graph.degree()))
    for i in range(len(new_graph.vs)):
        degree = new_graph.vs[i].degree()
        if degree>0:
            clustering_coeff_k[degree-1] += clustering_coeff_array[i]
            degree_hist[degree-1] += 1
    clustering_coeff_k = clustering_coeff_k/degree_hist
    return clustering_coeff_array, clustering_coeff_k
