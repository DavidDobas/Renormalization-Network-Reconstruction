import igraph as ig
import numpy as np
from tqdm import tqdm
from functools import cached_property 
from src import network_properties
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


def create_RM_graph(strengths, z, weighted=True, check_consistency = False):
    if weighted and check_consistency:
        check_weighted_consistency(strengths)
    if weighted:
        W = np.sum(strengths[:,0])
    n = len(strengths)
    graph = Graph_with_properties(n, edges=[], directed=True)
    edges_to_add = []
    weights_to_add = []
    random_numbers = np.random.random_sample([n,n])
    for i in range(n):
        for j in range(n):
            x_i = strengths[i][0]
            y_j = strengths[j][1]
            p_ij = 1 - np.exp(-z*x_i*y_j) if z < np.infty else 1
            if random_numbers[i][j] < p_ij:
                edges_to_add.append((i,j))
                if weighted:
                    weights_to_add.append(assign_weight(x_i, y_j, p_ij, W))
    graph.add_edges(edges_to_add)
    if weighted:
        graph.es["weight"] = weights_to_add
    return graph

def generate_RM_ensemble(n, strengths, z, weighted=True, parallel=True):
    if parallel:
        return Parallel(n_jobs=cpu_count())(delayed(create_RM_graph)(strengths, z, weighted) for i in tqdm(range(n)))
    return [create_RM_graph(strengths, z, weighted) for i in tqdm(range(n))]

# Assure that sum of outcoming strengths is the same as sum of incoming strengths
def make_strengths_consistent(strengths):
    new_strengths = np.copy(strengths)
    x_i_arr, y_i_arr = zip(*new_strengths)
    x_sum = np.sum(x_i_arr)
    y_sum = np.sum(y_i_arr)
    new_strengths[-1,1] = new_strengths[-1,1] + x_sum - y_sum
    return new_strengths