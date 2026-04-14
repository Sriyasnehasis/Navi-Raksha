#skeleton 👇
import pickle
import networkx as nx
import heapq
import math
import pandas as pd

#This is your heuristic function to estimate distance between two points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

#Load graph
def load_graph():
    with open("data/raw/navi_mumbai_road_graph.pkl", "rb") as f:
        G = pickle.load(f)
    return G

#Graph works with nodes, not lat/lon
def get_nearest_node(G, lat, lon):
    closest = None
    min_dist = float("inf")

    for node in G.nodes(data=True):
        n, data = node
        dist = haversine(lat, lon, data['y'], data['x'])
        if dist < min_dist:
            min_dist = dist
            closest = n

    return closest

#Add time-dependent edge weights
def add_traffic_weights_to_graph(G, hour, is_monsoon=False):
    """Add edge weights based on time of day and weather"""

    # Define traffic factors
    PEAK_HOURS = list(range(8, 10)) + list(range(17, 19))  # 8-10 AM, 5-7 PM
    NIGHT_HOURS = list(range(22, 24)) + list(range(0, 6))

    for u, v, data in G.edges(data=True):
        # Base length in km
        length_km = data.get('length_km', 1.0)
        if length_km == 0:
            length_km = 1.0

        # Determine base speed based on road type
        road_type = data.get('highway', 'residential')
        if road_type in ['motorway', 'trunk']:
            base_speed = 50  # km/h
        elif road_type in ['primary', 'secondary']:
            base_speed = 40
        else:
            base_speed = 30

        # Apply time-of-day factor
        if hour in PEAK_HOURS:
            speed_factor = 0.6  # 40% slower in peak hours
        elif hour in NIGHT_HOURS:
            speed_factor = 1.2  # 20% faster at night
        else:
            speed_factor = 1.0

        # Apply monsoon factor (if needed)
        if is_monsoon:
            speed_factor *= 0.75  # 25% slower in monsoon

        # Calculate travel time in minutes
        effective_speed = base_speed * speed_factor
        travel_time_min = (length_km / effective_speed * 60) if effective_speed > 0 else 10

        # Ambulance advantage: can use one-ways, shortcuts
        if data.get('oneway'):
            travel_time_min *= 0.95  # 5% faster

        # Add as edge weight
        data['travel_time'] = travel_time_min
        data['weight'] = travel_time_min

    return G

#Create zone-to-node mapping
def create_zone_to_node_mapping(G):
    locations_df = pd.read_csv('data/raw/key_locations.csv')
    print(locations_df.head())
    
    zone_to_node = {}

    for idx, row in locations_df.iterrows():
        zone_name = row['Unnamed: 0']  # Adjust column name as needed
        lat = row['lat']
        lon = row['lon']

        # Find nearest node in graph
        nearest_node = get_nearest_node(G, lat, lon)

        zone_to_node[zone_name] = nearest_node
        print(f"{zone_name} → Node {nearest_node}")

    return zone_to_node, locations_df

#A* Algorithm
def astar(G, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))

    came_from = {}
    cost_so_far = {start: 0}

    while queue:
        _, current = heapq.heappop(queue)

        if current == goal:
            break

        for neighbor in G.neighbors(current):
            # Use travel_time as weight
            weight = G[current][neighbor].get("travel_time", 1.0)

            new_cost = cost_so_far[current] + weight

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost

                heuristic = haversine(
                    G.nodes[neighbor]['y'],
                    G.nodes[neighbor]['x'],
                    G.nodes[goal]['y'],
                    G.nodes[goal]['x']
                )

                priority = new_cost + heuristic
                heapq.heappush(queue, (priority, neighbor))
                came_from[neighbor] = current

    return reconstruct_path(came_from, start, goal), cost_so_far.get(goal, float('inf'))

#Reconstruct path from A* search
def reconstruct_path(came_from, start, goal):
    current = goal
    path = []

    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return []

    path.append(start)
    path.reverse()
    return path

#Get top 3 routes
def optimize_route(source_lat, source_lon, dest_lat, dest_lon, hour=12, is_monsoon=False):
    G = load_graph()
    G = add_traffic_weights_to_graph(G, hour, is_monsoon)

    start = get_nearest_node(G, source_lat, source_lon)
    goal = get_nearest_node(G, dest_lat, dest_lon)

    route, travel_time = astar(G, start, goal)

    return route, travel_time

#Test it
if __name__ == "__main__":
    G = load_graph()
    print(f"Graph loaded:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    
    zone_to_node, locations_df = create_zone_to_node_mapping(G)
    print(f"\nZone mapping created: {len(zone_to_node)} zones")
    
    # Test routing
    route, travel_time = optimize_route(
        source_lat=locations_df.loc[locations_df['Unnamed: 0'] == 'Vashi_CBD_Main', 'lat'].values[0],
        source_lon=locations_df.loc[locations_df['Unnamed: 0'] == 'Vashi_CBD_Main', 'lon'].values[0],
        dest_lat=locations_df.loc[locations_df['Unnamed: 0'] == 'Belapur_Central', 'lat'].values[0],
        dest_lon=locations_df.loc[locations_df['Unnamed: 0'] == 'Belapur_Central', 'lon'].values[0],
        hour=14,
        is_monsoon=False
    )
    
    if route:
        print(f"✅ Route found!")
        print(f"  Path: {len(route)} nodes")
        print(f"  ETA: {travel_time:.2f} min")
    else:
        print("❌ No route found")