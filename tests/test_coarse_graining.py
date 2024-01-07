"""Tests for coarse_graining.py"""
import pytest
import igraph as ig
from src.coarse_graining import coarse_grain_strengths, coarse_grain_weighted_graph

@pytest.mark.parametrize(['strengths', 'group_sequence', 'expected'],
                [([[1,1], [2,1], [1,3]], [[0,1], [2]], [[3,2], [1,3]]),
                 ([[1,1], [2,1], [1,3]], [[0], [1], [2]], [[1,1], [2,1], [1,3]]),
                 ([[1,1], [2,2], [3,3]], [[0,1,2]], [[6,6]])]
)
def test_coarse_grain_strengths(strengths, group_sequence, expected):
    assert (coarse_grain_strengths(strengths, group_sequence) == expected).all()

initial_graph = ig.Graph(n=6, edges = [[0,1], [1,2], [2,3], [3,4], [4,2], [5,4]], directed=True)
initial_graph.es["weight"] = [1,2,2,4,3,6]
exp_final_graph = ig.Graph(n=3, edges=[[0,0], [0,1], [1,0], [1,1], [2,1]], directed=True)
exp_final_graph.es["weight"] = [3,2,3,4,6]
group_sequence = [[0,1,2], [3,4], [5]]
def test_coarse_grain_weighted_graph():
    final_graph = coarse_grain_weighted_graph(initial_graph, group_sequence)
    assert final_graph.vs.indices == exp_final_graph.vs.indices
    assert final_graph.get_edgelist() == exp_final_graph.get_edgelist()
    assert final_graph.es["weight"] == exp_final_graph.es["weight"]