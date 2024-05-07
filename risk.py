import os
import random
import time
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.collections import LineCollection

from src.init_graph import init_graph
from src.init_positions import positions_720p as positions

color_map = {
    1: "red",
    2: "blue",
    3: "green",
    4: "yellow",
    5: "purple",
    6: "orange",
}


class Board:
    """Create the board with a graph."""

    def __init__(self):
        self.graph = init_graph()

        plt.figure(figsize=(12.8, 7.2))
        plt.xlim([0, 1280])
        plt.ylim([0, 720])
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.axis("off")
        plt.ion()
        plt.show()
        img_path = os.path.join(os.path.dirname(__file__), "img", "risk_720p.png")
        img = plt.imread(img_path)
        plt.imshow(img, extent=[0, 1280, 0, 720], aspect="equal")

        self.nodes = nx.draw_networkx_nodes(
            self.graph,
            positions,
            node_size=2000,
            node_color=self.get_nodes_colors(),
            alpha=0.60,
            node_shape="o",
        )

        self.edges = nx.draw_networkx_edges(
            self.graph,
            positions,
            edgelist=self.get_edges_list(),
            width=1,
            edge_color="k",
            style="dotted",
        )

        self.troops = nx.draw_networkx_labels(
            self.graph,
            positions,
            font_size=12,
            font_color="black",
            font_weight="bold",
            labels=self.get_troops_dict(),
            verticalalignment="center",
            horizontalalignment="center",
            font_family="monospace",
        )

    def get_nodes_colors(self) -> List[str]:
        return [
            color_map[self.graph.nodes[node].get("owner", 1)]
            for node in self.graph.nodes
        ]

    def get_edges_list(self) -> List[Tuple[str, str]]:
        edges_list = [
            (u, v)
            for u, v in self.graph.edges
            if not (
                (u == "Alaska" and v == "Kamchatka")
                or (u == "Kamchatka" and v == "Alaska")
            )
        ]
        return edges_list

    def get_troops_dict(self) -> dict:
        return {node: self.graph.nodes[node]["troops"] for node in self.graph.nodes}

    def draw_nodes(self):
        if self.nodes:
            if isinstance(self.nodes, list):
                for coll in self.nodes:
                    coll.remove()
            else:
                self.nodes.remove()
        self.nodes = nx.draw_networkx_nodes(
            self.graph,
            positions,
            node_size=2000,
            node_color=self.get_nodes_colors(),
            alpha=0.60,
            node_shape="o",
        )

    def draw_edges(self):
        if self.edges:
            if isinstance(self.edges, list):
                for coll in self.edges:
                    coll.remove()
            else:
                self.edges.remove()
        self.edges = nx.draw_networkx_edges(
            self.graph,
            positions,
            edgelist=self.get_edges_list(),
            width=1,
            edge_color="k",
            style="dotted",
        )

    def draw_troops(self):
        if self.troops:
            for label in self.troops.values():
                label.remove()
        self.troops = nx.draw_networkx_labels(
            self.graph,
            positions,
            font_size=12,
            font_color="black",
            font_weight="bold",
            labels=self.get_troops_dict(),
            verticalalignment="center",
            horizontalalignment="center",
            font_family="monospace",
        )

    def draw_country_names(self):
        """Draw the country names as labels of the graph nodes with a formatted text."""
        formatted_labels = {node: "\n".join(node.split()) for node in self.graph.nodes}
        country_labels = nx.draw_networkx_labels(
            self.graph,
            positions,
            font_size=10,
            font_color="black",
            labels=formatted_labels,
            verticalalignment="center",
            horizontalalignment="center",
            font_family="monospace",
        )

    def update_troops(self, country, troops):
        """Change the number of troops in a country."""
        self.graph.nodes[country]["troops"] = troops
        self.draw_troops()

    def update_owner(self, country, owner):
        """Change the owner of a country."""
        self.graph.nodes[country]["owner"] = owner
        self.draw_nodes()

    def update_edge(self, edge):
        """Update an edge of the graph."""
        if self.edges:
            # print(self.edges)
            if isinstance(self.edges, list):
                for coll in self.edges:
                    if coll:
                        if type(coll) == LineCollection:
                            coll.remove()
                        else:
                            for line in coll:
                                line.remove()
            else:
                self.edges.remove()
        default_edges = [
            (u, v)
            for u, v in self.graph.edges
            if not (
                (u, v) == edge
                or (v, u) == edge
                or (u == "Alaska" and v == "Kamchatka")
                or (u == "Kamchatka" and v == "Alaska")
            )
        ]
        default_edges = nx.draw_networkx_edges(
            self.graph,
            positions,
            edgelist=default_edges,
            width=1,
            edge_color="k",
            style="dotted",
        )
        if isinstance(default_edges, list):
            for coll in default_edges:
                coll.set_zorder(1)
        else:
            default_edges.set_zorder(1)

        highlighted_edge = nx.draw_networkx_edges(
            self.graph,
            positions,
            edgelist=[edge],
            width=2,
            edge_color="r",
            style="solid",
            arrows=True,
            arrowsize=24,
            arrowstyle="-|>",
        )
        for coll in highlighted_edge:
            coll.set_zorder(3)

        self.edges = [default_edges, highlighted_edge]

    def randomize_country(self, country):
        """Randomize the number of troops in a country."""
        self.update_troops(country, random.randint(1, 10))
        self.update_owner(country, random.randint(1, 6))

    def randomize_board(self):
        """Randomize the number of troops in all countries."""
        for country in self.graph.nodes:
            self.randomize_country(country)


if __name__ == "__main__":
    board = Board()
    plt.pause(1)
    board.randomize_board()
    plt.pause(2)
    while True:
        board.update_edge(("Ukraine", "Afghanistan"))
        plt.pause(2)
        board.update_edge(("Afghanistan", "India"))
        plt.pause(2)
        break
