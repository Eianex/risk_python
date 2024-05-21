import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.animation import FuncAnimation

G = nx.Graph()

nodes = range(5)
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 3)]

G.add_nodes_from(nodes)
G.add_edges_from(edges)

pos = nx.spring_layout(G)

fig, ax = plt.subplots()

node_colors = ["skyblue"] * len(G.nodes)
edge_colors = ["gray"] * len(G.edges)

base_node_collection = nx.draw_networkx_nodes(
    G, pos, ax=ax, node_color=node_colors, node_size=300, node_shape="o"
)
base_edge_collection = nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors)
label_collection = nx.draw_networkx_labels(G, pos, ax=ax)

highlight_node = None
highlight_edges = None


def update(frame):
    global highlight_node, highlight_edges

    if highlight_node:
        highlight_node.remove()
    if highlight_edges:
        highlight_edges.remove()

    highlight_node = nx.draw_networkx_nodes(
        G, pos, nodelist=[3], ax=ax, node_color=np.random.rand(3,), node_size=600, node_shape="s"
    )

    highlight_edges = nx.draw_networkx_edges(
        G,
        pos,
        edgelist=[(u, v) for u, v in G.edges if u == 3 or v == 3],
        ax=ax,
        edge_color=np.random.rand(3,),
        width=2,
        style="dotted",
    )


ani = FuncAnimation(fig, update, frames=100, interval=20, repeat=False)
plt.show()
