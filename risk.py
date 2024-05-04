from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from src.init_graph import init_graph


class Board:
    """Create the board with a graph."""

    def __init__(self):
        self.graph = init_graph()

    def get_path_cost(self, path) -> int:
        """Calculate the total cost of a given path based on the troops in each country."""
        cost = int(0)
        for node in path:
            cost += int(self.graph.nodes[node]["troops"])
        return cost

    def find_least_resisted_path(self, start, goal) -> Tuple[List[str], int]:
        """Find the path with the least number of troops as resistance."""
        least_cost = float(1000000)
        best_path = [""]
        for path in nx.all_simple_paths(self.graph, source=start, target=goal):
            path: List[str] = list(path)
            current_cost = self.get_path_cost(self.graph, path)
            if current_cost < least_cost:
                least_cost = current_cost
                best_path = path

        return best_path, least_cost

    def draw_board(self):
        """Draw the board."""
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos, node_size=1200)
        nx.draw_networkx_edges(self.graph, pos, width=4)
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_family="sans-serif")
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    board = Board()
    board.draw_board()
