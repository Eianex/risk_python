import os
import random
import sys
import time
import warnings

import matplotlib

warnings.filterwarnings("ignore", category=UserWarning)
matplotlib.use("TkAgg")
matplotlib.rcParams["toolbar"] = "toolmanager"

import tkinter as tk
from typing import List, Tuple

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation
from matplotlib.backend_tools import ToolBase
from matplotlib.collections import LineCollection
from PIL import Image, ImageTk

from src.init_graph import init_graph
from src.positions import continents, positions

paused = False
color_map = {
    0: "white",  # "no owner"
    1: "red",
    2: "blue",
    3: "green",
    4: "yellow",
    5: "purple",
    6: "orange",
}


class Pause(ToolBase):
    image = os.path.join(os.path.dirname(__file__), "img", "pause.png")

    def trigger(self, sender, event, data=None):
        global paused
        paused = not paused


class Board:
    def __init__(self):
        self.graph = init_graph()
        self.deck_of_cards = self.fresh_deck_of_cards()
        self.game_turn = 0
        self.highlighted_country = None

        self.fig = plt.figure(figsize=(17.06, 7.2))
        self.fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1], figure=self.fig)
        self.board_ax = plt.subplot(gs[0])
        self.info_ax = plt.subplot(gs[1])
        plt.ion()

        self.canvas = self.fig.canvas
        self.canvas_manager = self.canvas.manager
        self.window = self.canvas_manager.window
        self.tool_manager = self.canvas_manager.toolmanager
        self.toolbar = self.canvas_manager.toolbar

        self.canvas.mpl_connect("close_event", self.handle_close)
        self.canvas_manager.set_window_title("Risk Simulator")

        screen_width, screen_height = self.get_screen_size()
        fig_width, fig_height = (1706, 720)
        fig_x = (screen_width // 2) - (fig_width // 2)
        fig_y = (screen_height // 2) - (fig_height // 2) - 50
        self.window.wm_geometry(f"+{fig_x}+{fig_y}")

        self.tool_manager.add_tool("pause", Pause)
        self.toolbar.add_tool(self.tool_manager.get_tool("pause"), "toolgroup")
        self.toolbar.pack_forget()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        icon_path = os.path.join(os.path.dirname(__file__), "img", "icon.png")
        icon_image = Image.open(icon_path)
        img_icon = ImageTk.PhotoImage(icon_image)
        self.window.tk.call("wm", "iconphoto", self.window._w, img_icon)

        img_path = os.path.join(os.path.dirname(__file__), "img", "risk_720p.png")
        img = plt.imread(img_path)
        self.board_ax.imshow(img, extent=[0, 1280, 0, 720], aspect="equal")

        self.nodes = self.draw_network_nodes()
        self.edges = self.draw_network_edges()
        self.troops = self.draw_network_lables()
        self.update_info_panel()

    @staticmethod
    def handle_close(evt):
        global paused
        paused = False
        sys.exit()

    @staticmethod
    def get_screen_size():
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height

    @staticmethod
    def dice_roll() -> int:
        return random.randint(1, 6)

    def get_card_type(self, country) -> int:
        if country == "Joker1" or country == "Joker2":
            return 0
        return self.graph.nodes[country]["card_type"]

    def fresh_deck_of_cards(self) -> dict:
        deck = {
            country: {
                "card_type": self.get_card_type(country),
                "card_owner": 0,
            }
            for country in self.graph.nodes
        }
        deck["Joker1"] = {"card_type": 0, "card_owner": 0}
        deck["Joker2"] = {"card_type": 0, "card_owner": 0}
        return deck

    def get_player_cards(self, player: int) -> list:
        return [
            card
            for card in self.deck_of_cards
            if self.deck_of_cards[card]["card_owner"] == player
        ]

    def calculate_bonus_troops(self, combination) -> int:
        bonus = 0
        cards_dict = {card: self.get_card_type(card) for card in combination}
        if len(set(cards_dict.values())) == 3:
            bonus = 10
        elif len(set(cards_dict.values())) == 1:
            card_type = list(cards_dict.values())[0]
            if card_type == 1:
                bonus = 4
            elif card_type == 2:
                bonus = 6
            elif card_type == 3:
                bonus = 8
        return bonus

    def cards_handler(self, player: int):
        players_cards = self.get_player_cards(player)
        n_cards = len(players_cards)
        bonus_troops = 0
        if n_cards >= 5:
            player_has_joker1 = "Joker1" in players_cards
            player_has_joker2 = "Joker2" in players_cards
            player_countries = self.get_player_countries(player)
            player_countries_with_card = []
            for country in player_countries:
                if country in players_cards:
                    player_countries_with_card.append(country)

            # Generate all the possible combinations of three cards 3 of the current player
            possible_combinations = []
            for i in range(n_cards):
                for j in range(i + 1, n_cards):
                    for k in range(j + 1, n_cards):
                        possible_combinations.append(
                            (players_cards[i], players_cards[j], players_cards[k])
                        )

            possible_combinations_bonus = {}
            # Go through all the possible combinations and check their corresponding troop bonuses, or absence of bonus (zero)
            for combination in possible_combinations:
                local_bonus_troops = self.calculate_bonus_troops(combination)
                possible_combinations_bonus[tuple(combination)] = local_bonus_troops
            # Sort the possible combinations by the bonus troops
            sorted_combinations = sorted(
                possible_combinations_bonus.items(), key=lambda x: x[1], reverse=True
            )
            maximum_bonus = sorted_combinations[0][1]
            # If the maximum bonus combination has a Joker in it, check if for the same bonus there is a combination without the Joker
            same_bonus_combos = [
                combination
                for combination, bonus in sorted_combinations
                if bonus == maximum_bonus
            ]
            # Check if there is more than 1 combination with the maximum bonus
            if len(same_bonus_combos) > 1:
                if player_has_joker1 or player_has_joker2:
                    for combination in same_bonus_combos:
                        if "Joker1" in combination or "Joker2" in combination:
                            same_bonus_combos.remove(combination)
                if same_bonus_combos:
                    maximum_bonus_combination = same_bonus_combos[0]
                else:
                    maximum_bonus_combination = random.choice(same_bonus_combos)
            else:
                maximum_bonus_combination = sorted_combinations[0][0]

            for card in maximum_bonus_combination:
                if card in player_countries_with_card:
                    self.update_troops(card, self.graph.nodes[card]["troops"] + 2)

            bonus_troops += possible_combinations_bonus[maximum_bonus_combination]
            for card in list(maximum_bonus_combination):
                self.deck_of_cards[card]["card_owner"] = 0

        return bonus_troops

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

    def draw_network_nodes(self):
        return nx.draw_networkx_nodes(
            self.graph,
            positions,
            node_size=2000,
            node_color=self.get_nodes_colors(),
            alpha=0.60,
            node_shape="o",
            ax=self.board_ax,
        )

    def draw_network_edges(self):
        return nx.draw_networkx_edges(
            self.graph,
            positions,
            edgelist=self.get_edges_list(),
            width=1,
            edge_color="k",
            style="dotted",
            ax=self.board_ax,
        )

    def draw_network_lables(self):
        return nx.draw_networkx_labels(
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

    def draw_nodes(self):
        if self.nodes:
            self.nodes.remove()
        self.nodes = self.draw_network_nodes()

    def draw_edges(self):
        if self.edges:
            if isinstance(self.edges, list):
                for coll in self.edges:
                    coll.remove()
            else:
                self.edges.remove()
        self.edges = self.draw_network_edges()

    def draw_troops(self):
        if self.troops:
            for label in self.troops.values():
                label.remove()
        self.troops = self.draw_network_lables()

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

    def update_troops(self, country, troops, interactive=True):
        """Change the number of troops in a country."""
        self.graph.nodes[country]["troops"] = troops
        if interactive:
            self.highlight_country(country)
            self.draw_troops()
            self.update_info_panel()

    def update_owner(self, country, owner, interactive=True):
        """Change the owner of a country."""
        self.graph.nodes[country]["owner"] = owner
        if interactive:
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
        if self.highlighted_country:
            self.highlighted_country.remove()
            self.highlighted_country = None

    def clear_highlighted_edge(self):
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
        self.update_troops(country, random.randint(1, 10))
        self.update_owner(country, random.randint(1, 6))

    def randomize_board(self):
        for country in self.graph.nodes:
            self.randomize_country(country)

    def populate_initial_board(self):
        list_of_countries = list(self.graph.nodes)
        random.shuffle(list_of_countries)

        # Select one random country for each player to start
        for player in range(1, 7):
            country = list_of_countries[player - 1]
            self.update_owner(country, player, interactive=False)
            self.update_troops(country, 1, interactive=False)

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
                    selected_country,
                    self.graph.nodes[selected_country]["troops"] + 1,
                    interactive=False,
                )
                players_troops[player] += 1

        self.draw_nodes()
        self.draw_troops()
        self.update_info_panel()
        plt.pause(0.1)

    def calculate_player_stats(self):
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

    def update_info_panel(self):
        self.info_ax.clear()
        self.info_ax.axis("off")
        player_data = self.calculate_player_stats()
        info_text = f"\n\nTURN: {self.game_turn}\n\n"
        for player, data in player_data.items():
            info_text += f"{player}. {str(color_map[player]).capitalize()} - Troops: {data['troops']}\nTerritories: {data['territories']}\n"

            player_cards = self.get_player_cards(player)
            last_two_cards = []
            if len(player_cards) == 0:
                info_text += f"Cards:\n\n\n\n"
            elif len(player_cards) <= 1:
                info_text += f"Cards: |{player_cards[0]}|\n\n\n\n"
            elif len(player_cards) == 2 or len(player_cards) == 3:
                first_card = player_cards[0]
                next_two_cards = player_cards[1:]
                info_text += (
                    f"Cards: |{first_card}|\n|{'| |'.join(next_two_cards)}|\n\n\n"
                )
            else:
                first_card = player_cards[0]
                next_two_cards = player_cards[1:3]
                last_two_cards = player_cards[3:]
                info_text += f"Cards: |{first_card}|\n|{'| |'.join(next_two_cards)}|\n|{'| |'.join(last_two_cards)}|\n\n"

        self.info_ax.text(
            0.14,
            0.5,
            info_text,
            transform=self.info_ax.transAxes,
            ha="left",
            va="center",
            fontsize=11,
            family="monospace",
        )

    def path_exists(self, origin: str, destination: str, owner: int) -> bool:
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
            if self.graph.nodes[country]["troops"] > 2
        ]
        if not countries_for_attack:
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
                    attacker_troops_left = self.graph.nodes[attacker]["troops"] - 1
                    leave_troops_behind = 0

                    if attacker_troops_left > 3:
                        leave_troops_behind = random.randint(0, 1)

                    self.update_owner(defender, self.graph.nodes[attacker]["owner"])
                    self.update_troops(
                        defender, attacker_troops_left - leave_troops_behind
                    )
                    self.update_troops(attacker, 1 + leave_troops_behind)
                    break

    def reinforce(self, player: int, after_elimination=False):
        reinforce_troops = 0
        if not after_elimination:
            reinforce_troops: int = self.get_bonus_troops(player)
            print(f"Player {player} has {reinforce_troops} troops to reinforce")
        player_countries = self.get_player_countries(player)
        if not player_countries:
            return
        cards_bonus = self.cards_handler(player)
        print(f"Player {player} got {cards_bonus} troops from cards")
        reinforce_troops += cards_bonus
        if cards_bonus and cards_bonus > 0:
            plt.pause(0.1)
        while reinforce_troops > 0:
            player_countries_copy = player_countries.copy()
            peaceful_destinations = [
                country
                for country in player_countries
                if all(
                    neighbour in player_countries
                    for neighbour in list(self.graph.neighbors(country))
                )
            ]
            if peaceful_destinations:
                for peaceful_destination in peaceful_destinations:
                    player_countries_copy.remove(peaceful_destination)

            if not player_countries_copy:
                return

            country = random.choice(player_countries_copy)
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

    def attack(self, player: int, already_card=False):
        possible_attacks = self.get_attacks(player)
        if not possible_attacks:
            return
        possible_attacks = random.sample(possible_attacks, len(possible_attacks))

        lowest_attack = (999, 999)
        lowest_names = ("", "")
        for pair_attack in possible_attacks:
            origin_troops = self.graph.nodes[pair_attack[0]]["troops"]
            destination_troops = self.graph.nodes[pair_attack[1]]["troops"]
            if destination_troops < lowest_attack[1] and origin_troops > 1:
                lowest_attack = (origin_troops, destination_troops)
                lowest_names = pair_attack

        origin, destination = lowest_names

        destination_neighbours = list(self.graph.neighbors(destination))

        player_countries_of_destination_neighbours = [
            country
            for country in destination_neighbours
            if self.graph.nodes[country]["owner"] == player
        ]

        maximum_troops_neighbour = ""
        if len(player_countries_of_destination_neighbours) > 1:
            maximum_troops_neighbour_player = 0
            for country in player_countries_of_destination_neighbours:
                troops = self.graph.nodes[country]["troops"]
                if troops > maximum_troops_neighbour_player:
                    maximum_troops_neighbour_player = troops
                    maximum_troops_neighbour = country
        if maximum_troops_neighbour and maximum_troops_neighbour != "":
            origin = maximum_troops_neighbour

        print(
            f"Player {player} is attacking from {origin} to {destination} with {self.graph.nodes[origin]['troops']} troops"
        )

        self.clear_highlighted_edge()
        self.clear_highlighted_country()
        plt.pause(0.1)
        self.highlight_country(origin)
        self.highlight_edge((origin, destination))
        plt.pause(0.1)
        destination_owner_before_attack = self.graph.nodes[destination]["owner"]
        self.roll_attack_once(origin, destination)
        destination_owner_after_attack = self.graph.nodes[destination]["owner"]
        plt.pause(0.1)
        self.clear_highlighted_edge()
        self.clear_highlighted_country()
        plt.pause(0.1)
        print("Attack done")

        if destination_owner_before_attack != destination_owner_after_attack:
            if self.get_player_countries(destination_owner_before_attack) == []:
                for card in self.get_player_cards(destination_owner_before_attack):
                    self.deck_of_cards[card]["card_owner"] = player
                self.reinforce(player, after_elimination=True)
                plt.pause(0.1)
                self.reinforce(player, after_elimination=True)
                plt.pause(0.1)

        # Check if the player conquered a country
        local_already_card = already_card
        if (self.graph.nodes[destination]["owner"] == player) and not already_card:
            # Change a random card owner but only cards which have not been assigned yet
            cards = [
                card
                for card in self.deck_of_cards
                if self.deck_of_cards[card]["card_owner"] == 0
            ]
            if cards:
                random_card = random.choice(cards)
                self.deck_of_cards[random_card]["card_owner"] = player
                print(f"Player {player} got the card {random_card}")
            local_already_card = True

        if (self.graph.nodes[destination]["owner"] == player) and (
            self.graph.nodes[origin]["troops"] > 2
        ):
            print(
                f"Player {player} conquered {destination} and has troops for attacking again.\n"
            )
            self.attack(player, already_card=local_already_card)

        # Check if the player has any country with more than 3 troops
        if any(
            self.graph.nodes[country]["troops"] > 3
            for country in self.get_player_countries(player)
        ):
            print(f"Player {player} can attack\n")
            self.attack(player, already_card=local_already_card)

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

        # Check wich destinations are surrounded by player's countries only
        peaceful_destinations = [
            country
            for country in destinations
            if all(
                neighbour in player_countries
                for neighbour in list(self.graph.neighbors(country))
            )
        ]
        if peaceful_destinations:
            # Remove peaceful_destinations from the possible destinations:
            for peaceful_destination in peaceful_destinations:
                destinations.remove(peaceful_destination)
        if not destinations:
            return
        origin_troops = self.graph.nodes[origin]["troops"]
        # Check if all origin neighbours are player's countries
        origin_peaceful = all(
            neighbour in player_countries
            for neighbour in list(self.graph.neighbors(origin))
        )
        lower_level_margin = 1
        if origin_peaceful and origin_troops > 3:
            lower_level_margin = origin_troops - 2

        destination = random.choice(destinations)
        n_troops = random.randint(lower_level_margin, origin_troops - 1)
        print(
            f"Player {player} is fortifying from {origin} to {destination} with {n_troops} troops"
        )
        self.clear_highlighted_country()
        self.clear_highlighted_edge()
        plt.pause(0.1)
        self.highlight_country(destination)
        self.highlight_edge_slightly((origin, destination))
        plt.pause(0.1)
        self.update_troops(origin, self.graph.nodes[destination]["troops"] - n_troops)
        self.update_troops(origin, self.graph.nodes[destination]["troops"] + n_troops)
        plt.pause(0.1)
        self.clear_highlighted_country()
        self.clear_highlighted_edge()
        plt.pause(0.1)
        print("Fortification done\n")

    def world_is_conquered(self) -> bool:
        players = [self.graph.nodes[country]["owner"] for country in self.graph.nodes]
        if len(set(players)) == 1:
            print(f"Player {players[0]} has conquered the world!")
            return True
        return False

    def game(self):
        self.populate_initial_board()
        self.game_turn += 1
        self.update_info_panel()
        plt.pause(0.1)
        while not self.world_is_conquered():
            for player in range(1, 7):
                self.reinforce(player)
                self.attack(player)
                self.fortify(player)
                self.update_info_panel()
                plt.pause(0.1)
            self.game_turn += 1
            self.update_info_panel()
            plt.pause(0.1)


if __name__ == "__main__":

    board = Board()
    board.game()
