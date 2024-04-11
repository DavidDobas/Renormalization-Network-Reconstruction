from tqdm import tqdm
from matplotlib import pyplot as plt
import igraph as ig
import numpy as np
from joblib import Parallel, delayed, cpu_count

def compute_property(graph, property, mode):
    return eval(f"graph.{property}(mode='{mode}')") if mode is not None else eval(f"graph.{property}()")

def plot_true_expected(original_graphs, ensembles, property, x_axis_strengths, mode=None, title=None, xlabel=None, ylabel=None, xscale=None, yscale=None, parallel=False):
    if parallel:
        exp_properties = [np.nanmean(Parallel(n_jobs=cpu_count())(delayed(compute_property)(graph, property, mode) for graph in tqdm(ensemble)), axis=0) for ensemble in ensembles]
    else:
        exp_properties = [np.nanmean([(eval(f"graph.{property}(mode='{mode}')") if mode is not None else eval(f"graph.{property}()")) for graph in tqdm(ensemble)], axis=0) for ensemble in ensembles]
    true_properties = [(eval(f"graph.{property}(mode='{mode}')") if mode is not None else eval(f"graph.{property}()")) for graph in original_graphs]
    num_graphs = len(original_graphs)
    fig, axs = plt.subplots(1, num_graphs, figsize=(20, 5))
    if title is not None: fig.suptitle(title)
    if ylabel is not None: axs[0].set(ylabel=ylabel)
    for i in range(num_graphs):
        axs[i].scatter(np.log10(x_axis_strengths[i]), true_properties[i], s=10, c="blue", alpha=.5)
        axs[i].scatter(np.log10(x_axis_strengths[i]), exp_properties[i], s=10, c="red", alpha=.5)
        axs[i].set(xlabel=xlabel)
        if xscale is not None: axs[i].set(xscale=xscale)
        if yscale is not None: axs[i].set(yscale=yscale)