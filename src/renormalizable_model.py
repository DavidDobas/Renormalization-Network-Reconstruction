import igraph as ig
import numpy as np
from tqdm import tqdm
from functools import cached_property 
from src import network_properties, utils
from joblib import Parallel, delayed, cpu_count

class Graph_with_properties(ig.Graph):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._degrees_out = None
        self._degrees_in = None
        self._strengths_out = None
        self._strengths_in = None
        self._annd_out = None
        self._annd_k_out = None
        self._annd_in = None
        self._annd_k_in = None
        self._anns_out = None
        self._anns_in = None
        self._cl_coeff = None
        self._cl_coeff_k = None
        self._weighted_cl_coeff = None

    def degrees(self, mode, recompute=False):
        if mode=="out":
            if self._degrees_out is None or recompute: self._degrees_out = self.degree(mode=mode)
            return self._degrees_out
        elif mode=="in":
            if self._degrees_in is None or recompute: self._degrees_in = self.degree(mode=mode)
            return self._degrees_in
        
    def strengths(self, mode, recompute=False):
        if mode=="out":
            if self._strengths_out is None or recompute: self._strengths_out = self.strength(mode=mode, weights=self.es["weight"])
            return self._strengths_out
        elif mode=="in":
            if self._strengths_in is None or recompute: self._strengths_in = self.strength(mode=mode, weights=self.es["weight"])
            return self._strengths_in

    def annd(self, mode, recompute=False):
        if mode=="out":
            if self._annd_out is None or recompute: self._annd_out, self._annd_k_out = network_properties.annd(self, mode=mode, len_deg_seq=self.vcount())
            return self._annd_out
        elif mode=="in":
            if self._annd_in is None or recompute: self._annd_in, self._annd_k_in = network_properties.annd(self, mode=mode, len_deg_seq=self.vcount())
            return self._annd_in
        
    def annd_k(self, mode, recompute=False):
        if mode=="out":
            if self._annd_out is None or recompute: self._annd_out, self._annd_k_out = network_properties.annd(self, mode=mode, len_deg_seq=self.vcount())
            return self._annd_k_out
        elif mode=="in":
            if self._annd_in is None or recompute: self._annd_in, self._annd_k_in = network_properties.annd(self, mode=mode, len_deg_seq=self.vcount())
            return self._annd_k_in
        
    def anns(self, mode, recompute=False):
        if mode=="out":
            if self._anns_out is None or recompute: self._anns_out = network_properties.anns(self, mode=mode)
            return self._anns_out
        elif mode=="in":
            if self._anns_in is None or recompute: self._anns_in = network_properties.anns(self, mode=mode)
            return self._anns_in
        
    def clustering_coeff(self, recompute=False):
        if self._cl_coeff is None or recompute: self._cl_coeff, self._cl_coeff_k = network_properties.clustering_coeff(self, len_deg_seq=self.vcount())
        return self._cl_coeff
    
    def clustering_coeff_k(self, recompute=False):
        if self._cl_coeff_k is None or recompute: self._cl_coeff, self._cl_coeff_k = network_properties.clustering_coeff(self, len_deg_seq=self.vcount())
        return self._cl_coeff_k
    
    def weighted_clustering_coeff(self, recompute=False):
        if self._weighted_cl_coeff is None or recompute: self._weighted_cl_coeff = network_properties.weighted_clustering_coeff(self)
        return self._weighted_cl_coeff


def assign_weight(x_i, y_j, p_ij, W):
    return x_i*y_j/(p_ij*W)

def check_weighted_consistency(strengths):
    x_i_array, y_i_array = zip(*strengths)
    if np.sum(x_i_array) != np.sum(y_i_array):
        raise Exception("Inconsistent weights")

def initialize_graph(strengths, weighted=True, check_consistency=False):
    if weighted and check_consistency:
        check_weighted_consistency(strengths)
    if weighted:
        W = np.sum(strengths[:,0])
    n = len(strengths)
    graph = Graph_with_properties(n, edges=[], directed=True)
    return graph, W, n

def convert_strengths_without_self_loops(strengths):
    out_strengths = strengths[:,0]
    in_strengths = strengths[:,1]
    S = np.sum(out_strengths)
    new_out_strengths = np.zeros(len(out_strengths))
    new_in_strengths = np.zeros(len(in_strengths))
    for i in range(len(out_strengths)):
        w_ii = out_strengths[i]*in_strengths[i]/S
        new_out_strengths[i] = out_strengths[i] + w_ii
        new_in_strengths[i] = in_strengths[i] + w_ii
    return np.stack([new_out_strengths, new_in_strengths], axis=1)    

# def create_RM_graph(strengths, z, weighted=True, check_consistency = False, self_loops = True):
#     if not self_loops:
#         new_strengths = convert_strengths_without_self_loops(strengths)
#     else:
#         new_strengths = strengths
#     graph, W, n = initialize_graph(new_strengths, weighted, check_consistency)
#     edges_to_add = []
#     weights_to_add = []
#     np.random.seed(2021)
#     random_numbers = np.random.random_sample([n,n])
#     for i in range(n):
#         for j in range(n):
#             if not self_loops and i==j:
#                 continue
#             else:
#                 x_i = new_strengths[i][0]
#                 y_j = new_strengths[j][1]
#                 p_ij = 1 - np.exp(-z*x_i*y_j) if z < np.infty else 1
#                 if random_numbers[i][j] < p_ij:
#                     edges_to_add.append((i,j))
#                     if weighted:
#                         weights_to_add.append(assign_weight(x_i, y_j, p_ij, W))
#     graph.add_edges(edges_to_add)
#     if weighted:
#         graph.es["weight"] = weights_to_add
#     return graph

def create_RM_graph(strengths, z, weighted=True, check_consistency=False, self_loops=True):
    if self_loops:
        new_strengths = strengths
    else:
        new_strengths = convert_strengths_without_self_loops(strengths)
    out_strengths = new_strengths[:,0]
    in_strengths = new_strengths[:,1]
    W = np.sum(out_strengths)
    num_nodes = len(out_strengths)
    prob_matrix = np.ones([num_nodes, num_nodes]) - np.exp(-z*out_strengths.reshape(num_nodes,1)@in_strengths.reshape(1,num_nodes))
    random_numbers = np.random.random_sample([num_nodes,num_nodes])
    if weighted:
        weight_matrix = out_strengths.reshape(num_nodes,1)@in_strengths.reshape(1,num_nodes)/(W*prob_matrix)
        weighted_adj_matrix = weight_matrix*(random_numbers<prob_matrix)
        return utils.graph_from_adjacency(weighted_adj_matrix, weighted=True)
    return utils.graph_from_adjacency(random_numbers<prob_matrix)

def create_naive_degree_corrected_RM_graph(strengths, z, weighted=True, check_consistency = False):
    graph, W, n = initialize_graph(strengths, weighted, check_consistency)
    edges_to_add = []
    weights_to_add = []
    random_numbers = np.random.random_sample([n,n])
    edges_to_add = []
    weights_to_add = []
    random_numbers = np.random.random_sample([n,n])
    for i in range(n):
        x_i = strengths[i][0]
        p_k_i_nonzero = 1-np.exp(-z*x_i*W)
        for j in range(n):
            y_j = strengths[j][1]
            p_ij = (1 - np.exp(-z*x_i*y_j))/p_k_i_nonzero if z < np.infty else 1
            if random_numbers[i][j] < p_ij:
                edges_to_add.append((i,j))
                if weighted:
                    weights_to_add.append(assign_weight(x_i, y_j, p_ij, W))
    graph.add_edges(edges_to_add)
    if weighted:
        graph.es["weight"] = weights_to_add
    return graph

def create_degree_corrected_RM_graph(strengths, z, weighted=True, check_consistency = False):
    graph, W, n = initialize_graph(strengths, weighted, check_consistency)
    edges_to_add = []
    weights_to_add = []
    random_numbers = np.random.random_sample([n,n])
    edges_to_add = []
    weights_to_add = []
    random_numbers = np.random.random_sample([n,n])
    for i in range(n):
        x_i = strengths[i][0]
        p_k_i_nonzero = 1-np.exp(-z*x_i*W)
        for j in range(n):
            y_j = strengths[j][1]
            p_ij = (1 - np.exp(-z*x_i*y_j))/p_k_i_nonzero if z < np.infty else 1
            if random_numbers[i][j] < p_ij:
                edges_to_add.append((i,j))
                if weighted:
                    weights_to_add.append(assign_weight(x_i, y_j, p_ij, W))
    graph.add_edges(edges_to_add)
    if weighted:
        graph.es["weight"] = weights_to_add
    return graph

def generate_RM_ensemble(n, strengths, z, weighted=True, degree_corrected = False, parallel=True, self_loops = True):
    if parallel:
        if degree_corrected:
            return Parallel(n_jobs=cpu_count())(delayed(create_naive_degree_corrected_RM_graph)(strengths, z, weighted) for _ in tqdm(range(n)))
        return Parallel(n_jobs=cpu_count())(delayed(create_RM_graph)(strengths, z, weighted=weighted, self_loops=self_loops) for _ in tqdm(range(n)))
    if degree_corrected:
        return [create_naive_degree_corrected_RM_graph(strengths, z, weighted) for _ in tqdm(range(n))]
    return [create_RM_graph(strengths, z, weighted=weighted, self_loops=self_loops) for _ in tqdm(range(n))]

# Assure that sum of outcoming strengths is the same as sum of incoming strengths
def make_strengths_consistent(strengths):
    new_strengths = np.copy(strengths)
    x_i_arr, y_i_arr = zip(*new_strengths)
    x_sum = np.sum(x_i_arr)
    y_sum = np.sum(y_i_arr)
    new_strengths[-1,1] = new_strengths[-1,1] + x_sum - y_sum
    return new_strengths