import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.animation import FuncAnimation


def draw_graph(pos):
    plt.clf()
    nx.draw(
        G, pos, with_labels=True, node_color="skyblue", node_size=700, edge_color="gray"
    )
    plt.title("Undirected Graph Animation")


nodes = range(5)
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 3)]

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

pos = {
    0: np.array([0.0, 0.0]),
    1: np.array([1.0, 1.0]),
    2: np.array([2.0, 2.0]),
    3: np.array([3.0, 3.0]),
    4: np.array([4.0, 4.0]),
}

fig, ax = plt.subplots()


def update(num, pos, ax: plt.Axes):
    ax.clear()
    draw_graph(pos)

    for node in pos:
        pos[node] += np.random.normal(0.01, 0.01, 2)


ani = FuncAnimation(fig, update, frames=100, fargs=(pos, ax), interval=10, repeat=False)

plt.show()
