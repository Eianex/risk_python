import os
import random
import time
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.collections import LineCollection, PatchCollection

from src.init_graph import init_graph
from src.positions import positions_720p as positions

color_map = {
    0: "white",  # "no owner"
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
        self.highlighted_country = None

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

        return [
            (u, v)
            for u, v in self.graph.edges
            if not (
                (u == "Alaska" and v == "Kamchatka")
                or (u == "Kamchatka" and v == "Alaska")
            )
        ]

    def get_troops_dict(self) -> dict:
        return {node: self.graph.nodes[node]["troops"] for node in self.graph.nodes}

    def draw_nodes(self):
        if self.nodes:
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
        self.highlight_country(country)
        self.draw_troops()

    def update_owner(self, country, owner):
        """Change the owner of a country."""
        self.graph.nodes[country]["owner"] = owner
        self.highlight_country(country)
        self.draw_nodes()

    def highlight_edge(self, edge):
        """Update an edge of the graph."""
        if self.edges:
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
            edge_color=color_map[self.graph.nodes[edge[0]]["owner"]],
            style="solid",
            arrows=True,
            arrowsize=24,
            arrowstyle="-|>",
        )
        for coll in highlighted_edge:
            coll.set_zorder(3)

        self.edges = [default_edges, highlighted_edge]

    def highlight_country(self, country):
        """Highlight a country in the board."""
        self.clear_highlighted_country()
        self.highlighted_country = nx.draw_networkx_nodes(
            self.graph,
            positions,
            nodelist=[country],
            node_size=2000,
            node_color=color_map[self.graph.nodes[country]["owner"]],
            alpha=0.8,
            edgecolors="black",
            linewidths=4,
            node_shape="o",
        )
        self.highlighted_country.set_zorder(1)

    def clear_highlighted_country(self):
        """Clear the highlighted country."""
        if self.highlighted_country:
            self.highlighted_country.remove()
            self.highlighted_country = None

    def clear_highlighted_edge(self):
        """Clear the highlighted edge."""
        if self.edges:
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
        self.edges = nx.draw_networkx_edges(
            self.graph,
            positions,
            edgelist=self.get_edges_list(),
            width=1,
            edge_color="k",
            style="dotted",
        )

    def randomize_country(self, country):
        """Randomize the number of troops in a country."""
        self.update_troops(country, random.randint(1, 10))
        self.update_owner(country, random.randint(1, 6))

    def randomize_board(self):
        """Randomize the number of troops in all countries."""
        for country in self.graph.nodes:
            self.randomize_country(country)

    def populate_initial_board(self):
        """Populate the board with the initial number of troops."""
        list_of_countries = list(self.graph.nodes)
        random.shuffle(list_of_countries)
        # Continue while all players have 20 troops
        while 0 in [
            self.graph.nodes[country]["owner"] for country in list_of_countries
        ]:
            for player in range(1, 7):
                for country in list_of_countries:
                    if self.graph.nodes[country]["owner"] == 0:
                        self.update_owner(country, player)
                        self.update_troops(country, 1)
                        plt.pause(0.01)
                        break
        players_troops = {
            player: sum(
                [
                    self.graph.nodes[country]["troops"]
                    for country in list_of_countries
                    if self.graph.nodes[country]["owner"] == player
                ]
            )
            for player in range(1, 7)
        }
        while min(players_troops.values()) < 20:
            players_less_than_20 = [
                player for player, troops in players_troops.items() if troops < 20
            ]
            player = random.choice(players_less_than_20)
            player_countries = [
                country
                for country in list_of_countries
                if self.graph.nodes[country]["owner"] == player
            ]
            random.shuffle(player_countries)
            first_country = player_countries[0]
            self.update_troops(
                first_country, self.graph.nodes[first_country]["troops"] + 1
            )
            players_troops[player] += 1
            plt.pause(0.01)


if __name__ == "__main__":
    board = Board()
    plt.pause(1)
    board.populate_initial_board()
    print("Initial board populated.")
    plt.pause(1)
    board.highlight_country("Ukraine")
    board.highlight_edge(("Ukraine", "Afghanistan"))
    plt.pause(1)
    board.highlight_country("India")
    board.highlight_edge(("India", "Afghanistan"))
    plt.pause(1)
    board.highlight_country("Siam")
    board.highlight_edge(("Siam", "Indonesia"))
    plt.pause(1)
    board.clear_highlighted_country()
    plt.pause(1)
    board.clear_highlighted_edge()
    plt.pause(1)
    board.highlight_country("Indonesia")
    board.highlight_edge(("Indonesia", "Siam"))
    plt.pause(10)
    plt.close()
