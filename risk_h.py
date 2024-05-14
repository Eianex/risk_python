import os
import random
import sys
from typing import List, Tuple

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.collections import LineCollection

from src.init_graph import init_graph
from src.positions import continents, positions

color_map = {
    0: "white",  # "no owner"
    1: "red",
    2: "blue",
    3: "green",
    4: "yellow",
    5: "purple",
    6: "orange",
}


def get_troops_updates(G1: nx.Graph, G2: nx.Graph) -> List[Tuple[str, int]]:
    country_names = list(G1.nodes)
    troops_updates = []
    print(f"{G1==G2}")
    for country in country_names:
        troops1 = G1.nodes[country]["troops"]
        troops2 = G2.nodes[country]["troops"]
        if troops1 != troops2:
            print(f"Troops in {country} changed from {troops1} to {troops2}")
            troops_updates.append((country, troops2))
    return troops_updates


def get_owner_updates(G1: nx.Graph, G2: nx.Graph) -> List[Tuple[str, int]]:
    country_names = list(G1.nodes)
    owner_updates = []
    for country in country_names:
        owner1 = G1.nodes[country]["owner"]
        owner2 = G2.nodes[country]["owner"]
        if owner1 != owner2:
            print(f"Owner of {country} changed from {owner1} to {owner2}")
            owner_updates.append((country, owner2))
    return owner_updates


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

    def highlight_edge_slightly(self, edge):
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
            style="dashed",
            arrows=True,
            arrowsize=24,
            arrowstyle="-|>",
            ax=self.board_ax,
        )
        for coll in highlighted_edge:
            coll.set_zorder(3)

        self.edges = [default_edges, highlighted_edge]

    def highlight_country(self, country):
        """Highlight a country in the self."""
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
            plt.pause(0.1)

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
                plt.pause(0.1)

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

    @staticmethod
    def dice_roll() -> int:
        return random.randint(1, 6)

    def path_exists(self, origin: str, destination: str, owner: int) -> bool:
        # nx.has_path(self.graph, origin, destination)
        # Analogous function to has_path but with the owner condition per connection between nodes
        visited = {origin}
        stack = [origin]
        while stack:
            node = stack.pop()
            if node == destination:
                return True
            for neighbour in self.graph.neighbors(node):
                if (
                    neighbour not in visited
                    and self.graph.nodes[neighbour]["owner"] == owner
                ):
                    visited.add(neighbour)
                    stack.append(neighbour)
        return False

    def get_player_countries(self, player: int) -> List[str]:
        all_countries = list(self.graph.nodes)
        player_countries = []
        for country in all_countries:
            owner_of_country = self.graph.nodes[country]["owner"]
            if owner_of_country == player:
                player_countries.append(country)
        print(f"Player {player} has countries {player_countries}")
        return player_countries

    def dice_rolls_defense(self, country: str) -> List[int]:
        if self.graph.nodes[country]["troops"] > 1:
            return [self.dice_roll(), self.dice_roll()]
        else:
            return [self.dice_roll()]

    def dice_rolls_attack(self, country: str) -> List[int]:
        if self.graph.nodes[country]["troops"] > 3:
            return [self.dice_roll(), self.dice_roll(), self.dice_roll()]
        elif self.graph.nodes[country]["troops"] == 3:
            return [self.dice_roll(), self.dice_roll()]
        else:
            return [self.dice_roll()]

    def get_player_continents(self, player: int) -> List:
        player_countries = self.get_player_countries(player)
        player_continents = []
        for continent, countries in continents.items():
            if all(country in player_countries for country in countries):
                player_continents.append(continent)
        return player_continents

    def get_bonus_troops(self, player: int) -> int:
        player_countries = self.get_player_countries(player)
        bonus_territories = max(3, len(player_countries) // 3)
        player_continents = self.get_player_continents(player)
        if len(player_continents) == 0:
            return bonus_territories
        bonus_per_continent = {
            "North America": 5,
            "South America": 2,
            "Europe": 5,
            "Africa": 3,
            "Asia": 7,
            "Australia": 2,
        }
        total_bonus = (
            sum(bonus_per_continent[continent] for continent in player_continents)
            + bonus_territories
        )
        return total_bonus

    def get_attacks(self, player) -> List[Tuple]:
        player_countries = self.get_player_countries(player)
        if not player_countries:
            print("No countries to attack from")
            return
        countries_for_attack = [
            country
            for country in player_countries
            if self.graph.nodes[country]["troops"] > 1
        ]
        if not countries_for_attack:
            # print("No countries to attack from")
            return []
        neighbour_pairs = [
            (country, neighbour)
            for country in countries_for_attack
            for neighbour in list(self.graph.neighbors(country))
            if self.graph.nodes[neighbour]["owner"] != player
        ]
        if not neighbour_pairs:
            return []
        return neighbour_pairs

    def roll_attack_once(self, attacker: str, defender: str):
        possible_attacks = self.get_attacks(self.graph.nodes[attacker]["owner"])
        if not possible_attacks or (attacker, defender) not in possible_attacks:
            return

        attacker_rolls = self.dice_rolls_attack(attacker)
        defender_rolls = self.dice_rolls_defense(defender)

        attacker_rolls.sort(reverse=True)
        defender_rolls.sort(reverse=True)

        for i in range(min(len(attacker_rolls), len(defender_rolls))):
            if self.graph.nodes[attacker]["troops"] == 1:
                break
            if attacker_rolls[i] < defender_rolls[i]:
                self.update_troops(attacker, self.graph.nodes[attacker]["troops"] - 1)
            else:
                if self.graph.nodes[defender]["troops"] > 1:
                    self.update_troops(
                        defender, self.graph.nodes[defender]["troops"] - 1
                    )
                else:
                    self.update_owner(defender, self.graph.nodes[attacker]["owner"])
                    self.update_troops(
                        defender, self.graph.nodes[attacker]["troops"] - 1
                    )
                    self.update_troops(attacker, 1)
                    break

    def fortify_graph(self, country1, country2, troops):
        self.update_troops(country1, self.graph.nodes[country1]["troops"] - troops)
        self.update_troops(country2, self.graph.nodes[country2]["troops"] + troops)

    def reinforce(self, player: int):
        reinforce_troops: int = self.get_bonus_troops(player)
        print(f"Player {player} has {reinforce_troops} troops to reinforce")
        player_countries = self.get_player_countries(player)
        if not player_countries:
            return
        while reinforce_troops > 0:
            country = random.choice(player_countries)
            troops = random.randint(1, reinforce_troops)
            reinforce_troops -= troops
            self.clear_highlighted_country()
            plt.pause(0.1)
            self.highlight_country(country)
            plt.pause(0.1)
            print(f"Player {player} is reinforcing {country} with {troops} troops")
            self.update_troops(country, self.graph.nodes[country]["troops"] + troops)
            plt.pause(0.1)
            self.clear_highlighted_country()
            plt.pause(0.1)
            print("Reinforcement done")

    def attack(self, player: int):
        possible_attacks = self.get_attacks(player)
        if not possible_attacks:
            return
        origin, destination = random.choice(possible_attacks)
        print(
            f"Player {player} is attacking from {origin} to {destination} with {self.graph.nodes[origin]['troops']} troops"
        )

        self.clear_highlighted_edge()
        self.clear_highlighted_country()
        plt.pause(0.1)
        self.highlight_country(origin)
        self.highlight_edge((origin, destination))
        plt.pause(0.1)
        self.roll_attack_once(origin, destination)
        plt.pause(0.1)
        self.clear_highlighted_edge()
        self.clear_highlighted_country()
        plt.pause(0.1)
        print("Attack done")
        # Check if the player conquered a country
        if self.graph.nodes[destination]["owner"] == player:
            # If so, attack again
            print(f"Player {player} conquered {destination} and can attack again\n")
            self.attack(player)
        # Check if origin has troops left to attack
        if self.graph.nodes[origin]["troops"] > 2:
            print(f"Player {player} can attack again from {origin}\n")
            self.attack(player)

    def fortify(self, player: int):
        player_countries = self.get_player_countries(player)
        if not player_countries:
            return
        countries_for_fortify = [
            country
            for country in player_countries
            if self.graph.nodes[country]["troops"] > 1
        ]
        if not countries_for_fortify:
            return
        origin = random.choice(countries_for_fortify)

        destinations = [
            country
            for country in player_countries
            if self.path_exists(origin, country, player) and country != origin
        ]
        if not destinations:
            return
        destination = random.choice(destinations)
        n_troops = random.randint(1, self.graph.nodes[origin]["troops"] - 1)
        print(
            f"Player {player} is fortifying from {origin} to {destination} with {n_troops} troops"
        )
        self.clear_highlighted_country()
        self.clear_highlighted_edge()
        plt.pause(0.1)
        self.highlight_country(destination)
        self.highlight_edge_slightly((origin, destination))
        plt.pause(0.1)
        self.fortify_graph(origin, destination, n_troops)
        plt.pause(0.1)
        self.clear_highlighted_country()
        self.clear_highlighted_edge()
        plt.pause(0.1)
        print("Fortification done\n")

    def turn(self, player: int):
        self.reinforce(player)
        print("\n")
        plt.pause(0.1)
        self.attack(player)
        print("\n")
        plt.pause(0.1)
        self.fortify(player)
        print("\n")
        plt.pause(0.1)

    def game(self):
        for turn in range(1000):
            for player in range(1, 7):
                self.turn(player)
                plt.pause(0.1)
                self.update_info_panel()
                plt.pause(0.1)


if __name__ == "__main__":

    board = Board()
    board.populate_initial_board()
    print("Initial board populated.")
    plt.pause(0.1)
    board.game()
    plt.pause(0.1)
