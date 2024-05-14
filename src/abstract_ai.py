from abc import ABC, abstractmethod

import networkx as nx


# Parent class for all AI classes
class AI(ABC):
    def __init__(self, G: nx.Graph):
        self.G = G

    @abstractmethod
    def reinforce(self):
        pass

    @abstractmethod
    def attack(self):
        pass

    @abstractmethod
    def fortify(self):
        pass
