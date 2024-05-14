import networkx as nx

# Card types:
# 1 - Infantry
# 2 - Cavalry
# 3 - Artillery

def init_graph(G=nx.Graph()) -> nx.Graph:
    G = nx.Graph()
    G.add_node("Afghanistan", troops=0, owner=0, card_type=1)
    G.add_node("Alaska", troops=0, owner=0, card_type=1)
    G.add_node("Alberta", troops=0, owner=0, card_type=1)
    G.add_node("Argentina", troops=0, owner=0, card_type=2)
    G.add_node("Brazil", troops=0, owner=0, card_type=3)
    G.add_node("Central America", troops=0, owner=0, card_type=2)
    G.add_node("China", troops=0, owner=0, card_type=2)
    G.add_node("Congo", troops=0, owner=0, card_type=2)
    G.add_node("East Africa", troops=0, owner=0, card_type=3)
    G.add_node("Eastern Australia", troops=0, owner=0, card_type=1)
    G.add_node("Egypt", troops=0, owner=0, card_type=1)
    G.add_node("Eastern United States", troops=0, owner=0, card_type=3)
    G.add_node("Great Britain", troops=0, owner=0, card_type=2)
    G.add_node("Greenland", troops=0, owner=0, card_type=2)
    G.add_node("Iceland", troops=0, owner=0, card_type=1)
    G.add_node("India", troops=0, owner=0, card_type=1)
    G.add_node("Indonesia", troops=0, owner=0, card_type=2)
    G.add_node("Irkutsk", troops=0, owner=0, card_type=1)
    G.add_node("Japan", troops=0, owner=0, card_type=1)
    G.add_node("Kamchatka", troops=0, owner=0, card_type=2)
    G.add_node("Madagascar", troops=0, owner=0, card_type=1)
    G.add_node("Middle East", troops=0, owner=0, card_type=3)
    G.add_node("Mongolia", troops=0, owner=0, card_type=3)
    G.add_node("New Guinea", troops=0, owner=0, card_type=2)
    G.add_node("North Africa", troops=0, owner=0, card_type=1)
    G.add_node("Northern Europe", troops=0, owner=0, card_type=2)
    G.add_node("Northwest Territory", troops=0, owner=0, card_type=3)
    G.add_node("Ontario", troops=0, owner=0, card_type=3)
    G.add_node("Peru", troops=0, owner=0, card_type=2)
    G.add_node("Quebec", troops=0, owner=0, card_type=3)
    G.add_node("Scandinavia", troops=0, owner=0, card_type=3)
    G.add_node("Siam", troops=0, owner=0, card_type=3)
    G.add_node("Siberia", troops=0, owner=0, card_type=3)
    G.add_node("South Africa", troops=0, owner=0, card_type=3)
    G.add_node("Southern Europe", troops=0, owner=0, card_type=2)
    G.add_node("Ukraine", troops=0, owner=0, card_type=3)
    G.add_node("Ural", troops=0, owner=0, card_type=2)
    G.add_node("Venezuela", troops=0, owner=0, card_type=3)
    G.add_node("Western Australia", troops=0, owner=0, card_type=3)
    G.add_node("Western Europe", troops=0, owner=0, card_type=1)
    G.add_node("Western United States", troops=0, owner=0, card_type=1)
    G.add_node("Yakutsk", troops=0, owner=0, card_type=2)
    

    G.add_edge("Alaska", "Northwest Territory")
    G.add_edge("Alaska", "Alberta")
    G.add_edge("Alaska", "Kamchatka")
    G.add_edge("Northwest Territory", "Greenland")
    G.add_edge("Northwest Territory", "Alberta")
    G.add_edge("Northwest Territory", "Ontario")
    G.add_edge("Greenland", "Ontario")
    G.add_edge("Greenland", "Quebec")
    G.add_edge("Greenland", "Iceland")
    G.add_edge("Alberta", "Ontario")
    G.add_edge("Alberta", "Western United States")
    G.add_edge("Ontario", "Quebec")
    G.add_edge("Ontario", "Western United States")
    G.add_edge("Ontario", "Eastern United States")
    G.add_edge("Quebec", "Eastern United States")
    G.add_edge("Western United States", "Eastern United States")
    G.add_edge("Western United States", "Central America")
    G.add_edge("Eastern United States", "Central America")
    G.add_edge("Central America", "Venezuela")
    G.add_edge("Venezuela", "Peru")
    G.add_edge("Venezuela", "Brazil")
    G.add_edge("Peru", "Brazil")
    G.add_edge("Peru", "Argentina")
    G.add_edge("Brazil", "Argentina")
    G.add_edge("Brazil", "North Africa")
    G.add_edge("North Africa", "Western Europe")
    G.add_edge("North Africa", "Southern Europe")
    G.add_edge("North Africa", "Egypt")
    G.add_edge("North Africa", "East Africa")
    G.add_edge("Western Europe", "Great Britain")
    G.add_edge("Western Europe", "Northern Europe")
    G.add_edge("Western Europe", "Southern Europe")
    G.add_edge("Great Britain", "Iceland")
    G.add_edge("Great Britain", "Scandinavia")
    G.add_edge("Great Britain", "Northern Europe")
    G.add_edge("Scandinavia", "Iceland")
    G.add_edge("Scandinavia", "Northern Europe")
    G.add_edge("Scandinavia", "Ukraine")
    G.add_edge("Northern Europe", "Southern Europe")
    G.add_edge("Northern Europe", "Ukraine")
    G.add_edge("Southern Europe", "Ukraine")
    G.add_edge("Southern Europe", "Middle East")
    G.add_edge("Southern Europe", "Egypt")
    G.add_edge("Egypt", "East Africa")
    G.add_edge("Egypt", "Middle East")
    G.add_edge("East Africa", "Middle East")
    G.add_edge("East Africa", "Congo")
    G.add_edge("East Africa", "South Africa")
    G.add_edge("East Africa", "Madagascar")
    G.add_edge("Congo", "South Africa")
    G.add_edge("Congo", "North Africa")
    G.add_edge("South Africa", "Madagascar")
    G.add_edge("Ural", "Siberia")
    G.add_edge("Ural", "China")
    G.add_edge("Ural", "Afghanistan")
    G.add_edge("Ural", "Ukraine")
    G.add_edge("Siberia", "Yakutsk")
    G.add_edge("Siberia", "Irkutsk")
    G.add_edge("Siberia", "China")
    G.add_edge("Yakutsk", "Kamchatka")
    G.add_edge("Yakutsk", "Irkutsk")
    G.add_edge("Kamchatka", "Irkutsk")
    G.add_edge("Kamchatka", "Mongolia")
    G.add_edge("Kamchatka", "Japan")
    G.add_edge("Irkutsk", "Mongolia")
    G.add_edge("Mongolia", "China")
    G.add_edge("Mongolia", "Japan")
    G.add_edge("Afghanistan", "China")
    G.add_edge("Afghanistan", "Middle East")
    G.add_edge("Afghanistan", "India")
    G.add_edge("Afghanistan", "Ukraine")
    G.add_edge("China", "India")
    G.add_edge("China", "Siam")
    G.add_edge("Middle East", "India")
    G.add_edge("Middle East", "Ukraine")
    G.add_edge("India", "Siam")
    G.add_edge("Siam", "Indonesia")
    G.add_edge("Indonesia", "New Guinea")
    G.add_edge("Indonesia", "Western Australia")
    G.add_edge("New Guinea", "Western Australia")
    G.add_edge("New Guinea", "Eastern Australia")
    G.add_edge("Western Australia", "Eastern Australia")

    return G
