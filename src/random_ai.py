# Basic random AI for testing purposes

import random
from typing import Dict, List, Tuple

import networkx as nx

from src.abstract_ai import AI
from src.interactions import Interactions


class RandomAI(AI):
    def __init__(self, G: nx.Graph):
        super().__init__(G)
        self.G: nx.Graph = self.G

    def take_turn(self, player: int):
        self.reinforce(player, Interactions.get_bonus_troops(self.G, player))
        self.attack(player)
        self.fortify(player)

    def reinforce(self, player: int, reinforce_troops: int):
        player_countries = Interactions.get_player_countries(self.G, player)
        while reinforce_troops > 0:
            country = random.choice(player_countries)
            troops = random.randint(1, reinforce_troops)
            self.G.nodes[country]["troops"] += troops
            reinforce_troops -= troops

    def attack(self, player: int):
        possible_attacks = Interactions.get_attacks(self.G, player)
        if not possible_attacks:
            return
        origin, destination = random.choice(possible_attacks)
        self.G = Interactions.attack(self.G, origin, destination)

        probability_of_attack = 0.5

        new_attacks = Interactions.get_attacks(self.G, player)
        if not new_attacks:
            return
        new_origin, new_destination = random.choice(new_attacks)
        if random.random() < probability_of_attack:
            self.G = Interactions.attack(self.G, new_origin, new_destination)

    def fortify(self, player: int):
        player_countries = Interactions.get_player_countries(self.G, player)
        countries_for_fortify = [
            country
            for country in player_countries
            if self.G.nodes[country]["troops"] > 1
        ]
        if not countries_for_fortify:
            return
        origin = random.choice(countries_for_fortify)

        destinations = [
            country
            for country in player_countries
            if Interactions.path_exists(self.G, origin, country) and country != origin
        ]
        if not destinations:
            return
        destination = random.choice(destinations)
        n_troops = random.randint(1, self.G.nodes[origin]["troops"] - 1)
        self.G = Interactions.fortify(self.G, origin, destination, n_troops)
