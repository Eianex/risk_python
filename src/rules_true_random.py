# This file establishes the rules for the interactions of a true random Risk game mode.

import random
from typing import Dict, List, Tuple


def dice_roll():
    return random.randint(1, 6)


def get_defense_rolls(country) -> List[int]:
    if country["troops"] > 1:
        return [dice_roll(), dice_roll()]
    else:
        return [dice_roll()]


def get_attack_rolls(country) -> List[int]:
    if country["troops"] > 3:
        return [dice_roll(), dice_roll(), dice_roll()]
    elif country["troops"] == 3:
        return [dice_roll(), dice_roll()]
    else:
        return [dice_roll()]


def attack(attacker, defender) -> Tuple:
    attacker_rolls = get_attack_rolls(attacker)
    defender_rolls = get_defense_rolls(defender)

    attacker_rolls.sort(reverse=True)
    defender_rolls.sort(reverse=True)

    for i in range(min(len(attacker_rolls), len(defender_rolls))):
        if attacker_rolls[i] > defender_rolls[i]:
            defender["troops"] -= 1
        else:
            attacker["troops"] -= 1

    return attacker, defender


def move_troops(country1, country2, troops) -> Tuple:
    country1["troops"] -= troops
    country2["troops"] += troops

    return country1, country2
