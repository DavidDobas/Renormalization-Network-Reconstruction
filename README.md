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
#Fully connewcted graph
g3 = renormalizable_model.create_RM_graph(strengths, z=np.infty)
```

Generate ensemble of desired size
```python
ensemble_size = 1000
z=1
renormalizable_model.generate_RM_ensemble(ensemble_size, strengths, z)
```
