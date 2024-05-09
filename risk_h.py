import os
import random
import sys
from typing import List, Tuple

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.collections import LineCollection

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
        self.fig = plt.figure(figsize=(17.06, 7.2))
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1], figure=self.fig)
        self.board_ax = plt.subplot(gs[0])
        self.info_ax = plt.subplot(gs[1])
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.ion()

        self.board_ax.set_xlim([0, 1280])
        self.board_ax.set_ylim([0, 720])
        self.board_ax.axis("off")
        img_path = os.path.join(os.path.dirname(__file__), "img", "risk_720p.png")
        img = plt.imread(img_path)
        self.board_ax.imshow(img, extent=[0, 1280, 0, 720], aspect="equal")
        self.info_ax.axis("off")
        self.fig.canvas.mpl_connect("close_event", self.handle_close)

        self.nodes = nx.draw_networkx_nodes(
            self.graph,
            positions,
            node_size=2000,
            node_color=self.get_nodes_colors(),
            alpha=0.60,
            node_shape="o",
            ax=self.board_ax,
        )

        self.edges = nx.draw_networkx_edges(
            self.graph,
            positions,
            edgelist=self.get_edges_list(),
            width=1,
            edge_color="k",
            style="dotted",
            ax=self.board_ax,
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
            ax=self.board_ax,
        )
        self.update_info_panel()

    def handle_close(self, evt):
        sys.exit()

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
            ax=self.board_ax,
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
            ax=self.board_ax,
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
            ax=self.board_ax,
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
            ax=self.board_ax,
        )

    def update_troops(self, country, troops):
        """Change the number of troops in a country."""
        self.graph.nodes[country]["troops"] = troops
        self.highlight_country(country)
        self.draw_troops()
        self.update_info_panel()

    def update_owner(self, country, owner):
        """Change the owner of a country."""
        self.graph.nodes[country]["owner"] = owner
        self.highlight_country(country)
        self.draw_nodes()
        self.update_info_panel()

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
            ax=self.board_ax,
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
            ax=self.board_ax,
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
            ax=self.board_ax,
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
            ax=self.board_ax,
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

        # Select one random country for each player to start
        for player in range(1, 7):
            country = list_of_countries[player - 1]
            self.update_owner(country, player)
            self.update_troops(country, 1)
            plt.pause(0.01)

        # Keep track of the number of troops for each player
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

        # Add troops to countries until each player has 20 troops
        while min(players_troops.values()) < 20:
            players_less_than_20 = [
                player for player, troops in players_troops.items() if troops < 20
            ]
            for player in players_less_than_20:
                available_countries = [
                    country
                    for country in list_of_countries
                    if self.graph.nodes[country]["owner"] == player
                    or self.graph.nodes[country]["owner"] == 0
                ]
                random.shuffle(available_countries)
                selected_country = available_countries[
                    random.randint(0, len(available_countries) - 1)
                ]

                if self.graph.nodes[selected_country]["owner"] == 0:
                    self.update_owner(selected_country, player)

                self.update_troops(
                    selected_country, self.graph.nodes[selected_country]["troops"] + 1
                )
                players_troops[player] += 1
                plt.pause(0.01)

    def update_info_panel(self):
        self.info_ax.clear()
        self.info_ax.axis("off")
        player_data = self.calculate_player_stats()
        info_text = ""
        for player, data in player_data.items():
            info_text += f"PLAYER {player}: {str(color_map[player]).capitalize()}\nTroops: {data['troops']}\nTerritories: {data['territories']}\n\n"
        self.info_ax.text(
            0.5,
            0.5,
            info_text,
            transform=self.info_ax.transAxes,
            ha="center",
            va="center",
            fontsize=14,
            family="monospace",
        )

    def calculate_player_stats(self):
        """Calculate troops and territories for each player."""
        stats = {}
        for player in range(1, 7):
            territories = [
                node
                for node in self.graph.nodes
                if self.graph.nodes[node].get("owner") == player
            ]
            troops = sum(self.graph.nodes[node]["troops"] for node in territories)
            stats[player] = {"troops": troops, "territories": len(territories)}
        return stats


if __name__ == "__main__":
    board = Board()
    board.populate_initial_board()
    print("Initial board populated.")
    plt.pause(0.1)
    board.highlight_country("Ukraine")
    board.highlight_edge(("Ukraine", "Afghanistan"))
    plt.pause(0.1)
    board.highlight_country("India")
    board.highlight_edge(("India", "Afghanistan"))
    plt.pause(0.1)
    board.highlight_country("Siam")
    board.highlight_edge(("Siam", "Indonesia"))
    plt.pause(0.1)
    board.clear_highlighted_country()
    plt.pause(0.1)
    board.clear_highlighted_edge()
    plt.pause(0.1)
    board.highlight_country("Indonesia")
    board.highlight_edge(("Indonesia", "Siam"))
    plt.pause(10)
    plt.close()
