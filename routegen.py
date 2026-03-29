import osmnx as ox
import networkx as nx
import json

# Define origin and destination coordinates manually
origin = (13.037455471481548, 80.1345358364268)      # Iyyappanthangal Bus Depot
destination = (12.98704988577527, 80.25930075361671)
 # Vadapalani Bus Terminus

# Download road network around Chennai
G = ox.graph_from_point(origin, dist=20000, network_type='drive')

# Find nearest road nodes
orig_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
dest_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

# Compute shortest road route
route = nx.shortest_path(G, orig_node, dest_node, weight='length')

# Extract route coordinates
route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]

# Save to JSON
route_data = {
    "label": "Iyyappanthangal ↔ Thiruvamiyur Corridor",
    "color": "blue",
    "coordinates": route_coords
}

with open("thiruvanmiyur_route.json", "w") as f:
    json.dump(route_data, f, indent=4)

print("Route saved successfully!")