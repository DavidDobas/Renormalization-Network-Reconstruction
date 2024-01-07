#
This is a project implementing network reconstruction using a renormalizable network model. The model is defined in

*Garuccio, E., Lalli, M., & Garlaschelli, D.* (2023). **Multiscale network renormalization: Scale-invariance without geometry**. Phys. Rev. Res., 5, 043101.
[![DOI:10.1103/PhysRevResearch.5.043101](https://link.aps.org/doi/10.1103/PhysRevResearch.5.043101)
Garuccio, E., Lalli, M., & Garlaschelli, D. (2023). Multiscale network renormalization: Scale-invariance without geometry. Phys. Rev. Res., 5, 043101.
## Example usage

First we import all necessary packages and modules.

```python
import igraph as ig
import numpy as np
from src import renormalizable_model
```

Create graphs using renormalizable model
```python
strengths = [(1,1), (0,1), (0,0), (50, 50)]
n=len(strengths)
# Fully disconnected graph
g1 = renormalizable_model.create_RM_graph(strengths, z=0)
# Heterogenous graph
g2 = renormalizable_model.create_RM_graph(strengths, z=1)
#Fully connected graph
g3 = renormalizable_model.create_RM_graph(strengths, z=np.infty)
```

Generate ensemble of desired size
```python
ensemble_size = 1000
z=1
renormalizable_model.generate_RM_ensemble(ensemble_size, strengths, z)
```

Instances of graphs inherit all properites of igraph implementation, but also custom computations of network properties. Supported properties are:
- `graph.degrees(mode)` - mode can be "out" on "in" (holds for all other functions)
- `graph.strengths(mode)`
- `graph.annd(mode)` - average nearest neighbor degree
- `graph.annd_k(mode)` - average nearest neighbor degree, depending on degree `k`, averaged for every value of `k`
- `graph.anns(mode)` - average nearets neighbor strength
- `graph.clustering_coeff()` - clustering coefficient
- `graph.clustering_coeff_k()` - clustering coefficient depending on degree `k`
- `graph.weighted_clustering_coeff()`

The properties are computed once and then stored. If needed, one can use `recompute=True`, for example `graph.degrees(mode="out", recompute=True)`

Coarse-graining can be done
