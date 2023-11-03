import pytest
import igraph as ig
import numpy as np
from src.renormalizable_model import check_weighted_consistency, create_RM_graph, generate_RM_ensemble, make_strenghts_consistent

def test_check_weighted_consistency():
    strenghts = [[1,2], [2,1], [3,4]]
    with pytest.raises(Exception) as e_info:
        check_weighted_consistency(strenghts)
    strenghts = [[1,2], [2,1], [3,3]]
    check_weighted_consistency(strenghts)


expected_1 = ig.Graph(3, edges=[])
expected_2 = ig.Graph.Full(n=3, directed=True, loops=True)
expected_3 = ig.Graph.Full(n=3, directed=True, loops=True)
expected_3.es["weight"] = [1/6, 1/3, 1/2, 1/3, 2/3, 1, 1/2, 1, 3/2]
@pytest.mark.parametrize(['strenghts', 'z', 'weighted', 'expected'],
                [([[1,1], [2,1], [1,3]], 0, False, expected_1),
                 ([[1,1], [2,1], [1,3]], np.infty, False, expected_2),
                 ([[1,1], [2,2], [3,3]], np.infty, True, expected_3)]
)
def test_create_RM_graph(strenghts, z, weighted, expected):
    graph = create_RM_graph(strenghts, z, weighted)
    assert graph.vs.indices == expected.vs.indices
    assert graph.get_edgelist() == expected.get_edgelist()
    if weighted:
        assert graph.es["weight"] == expected.es["weight"]