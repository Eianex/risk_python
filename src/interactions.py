# This file establishes the rules for the interactions of a true random Risk game mode.

import random
from typing import Dict, List, Tuple

import networkx as nx

from src.positions import continents


class Interactions:

    @staticmethod
    def dice_roll() -> int:
        return random.randint(1, 6)

    @staticmethod
    def path_exists(G: nx.Graph, origin: str, destination: str) -> bool:
        return nx.has_path(G, origin, destination)

    @staticmethod
    def get_player_countries(G: nx.Graph, player: int) -> List[str]:
        return [
            country for country in list(G.nodes) if G.nodes[country]["owner"] == player
        ]

    @classmethod
    def dice_rolls_defense(cls, G: nx.Graph, country: str) -> List[int]:
        if G.nodes[country]["troops"] > 1:
            return [cls.dice_roll(), cls.dice_roll()]
        else:
            return [cls.dice_roll()]

    @classmethod
    def dice_rolls_attack(cls, G: nx.Graph, country: str) -> List[int]:
        if G.nodes[country]["troops"] > 3:
            return [cls.dice_roll(), cls.dice_roll(), cls.dice_roll()]
        elif G.nodes[country]["troops"] == 3:
            return [cls.dice_roll(), cls.dice_roll()]
        else:
            return [cls.dice_roll()]

    @classmethod
    def get_player_continents(cls, G: nx.Graph, player: int) -> List:
        player_countries = cls.get_player_countries(G, player)
        player_continents = []
        for continent, countries in continents.items():
            if all(country in player_countries for country in countries):
                player_continents.append(continent)
        return player_continents

    @classmethod
    def get_bonus_troops(cls, G: nx.Graph, player: int) -> int:
        player_countries = cls.get_player_countries(G, player)
        bonus_territories = max(3, len(player_countries) // 3)
        player_continents = cls.get_player_continents(G, player)
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

    @classmethod
    def get_attacks(cls, G: nx.Graph, player) -> List[Tuple]:
        player_countries = cls.get_player_countries(G, player)
        countries_for_attack = [
            country for country in player_countries if G.nodes[country]["troops"] > 1
        ]
        if not countries_for_attack:
            return []
        neighbour_pairs = [
            (country, neighbour)
            for country in countries_for_attack
            for neighbour in list(G.neighbors(country))
            if G.nodes[neighbour]["owner"] != player
        ]
        if not neighbour_pairs:
            return []
        return neighbour_pairs

    @classmethod
    def attack(cls, G: nx.Graph, attacker: str, defender: str) -> nx.Graph:
        possible_attacks = cls.get_attacks(G, attacker)
        if not possible_attacks or (attacker, defender) not in possible_attacks:
            return G

        attacker_rolls = cls.dice_rolls_attack(G, attacker)
        defender_rolls = cls.dice_rolls_defense(G, defender)

        attacker_rolls.sort(reverse=True)
        defender_rolls.sort(reverse=True)

        # Roll the dices, update troops and the Owner of the country
        # Leave 1 troop in the country of the attacker if it wins
        for i in range(min(len(attacker_rolls), len(defender_rolls))):
            if attacker_rolls[i] > defender_rolls[i]:
                G.nodes[defender]["troops"] -= 1
            else:
                G.nodes[attacker]["troops"] -= 1
        if G.nodes[defender]["troops"] == 0:
            G.nodes[defender]["owner"] = G.nodes[attacker]["owner"]
            G.nodes[attacker]["troops"] = 1
            G.nodes[defender]["troops"] = G.nodes[attacker]["troops"] - 1

        return G

    @classmethod
    def fortify(cls, G: nx.Graph, country1, country2, troops) -> nx.Graph:
        if cls.path_exists(G, country1, country2):
            G.nodes[country1]["troops"] -= troops
            G.nodes[country2]["troops"] += troops
        return G
