import pickle
import networkx as nx
import pandas as pd
from datetime import datetime
import heapq
import math

class AStarRouter:
    """A* pathfinding with ETA prediction"""

    def __init__(self, G, rf_model=None, scaler=None):
        self.G = G
        self.rf_model = rf_model
        self.scaler = scaler

    def heuristic(self, node1, node2):
        """Euclidean distance heuristic"""
        lat1, lon1 = self.G.nodes[node1].get('y', 0), self.G.nodes[node1].get('x', 0)
        lat2, lon2 = self.G.nodes[node2].get('y', 0), self.G.nodes[node2].get('x', 0)

        # Approximate distance in km
        dlat = (lat2 - lat1) * 111  # 1 degree ≈ 111 km
        dlon = (lon2 - lon1) * 111 * math.cos(math.radians(lat1))

        return math.sqrt(dlat**2 + dlon**2)

    def find_route(self, source_node, dest_node, hour=12, is_monsoon=False):
        """Find fastest route using A*"""

        # Add current time weights to graph
        self.add_traffic_weights_to_graph(hour, is_monsoon)

        # A* search
        open_set = [(0, source_node)]  # (f_score, node)
        came_from = {}
        g_score = {node: float('inf') for node in self.G.nodes()}
        g_score[source_node] = 0

        closed_set = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current in closed_set:
                continue

            if current == dest_node:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()

                return path, g_score[dest_node]

            closed_set.add(current)

            # Explore neighbors
            for neighbor in self.G.neighbors(current):
                if neighbor in closed_set:
                    continue

                edge_data = self.G[current][neighbor]
                travel_time = edge_data.get('travel_time', 1.0)

                tentative_g = g_score[current] + travel_time

                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, dest_node)
                    heapq.heappush(open_set, (f_score, neighbor))

        return None, float('inf')  # No path found

    def add_traffic_weights_to_graph(self, hour, is_monsoon=False):
        """Add edge weights based on time of day and weather"""

        # Define traffic factors
        PEAK_HOURS = list(range(8, 10)) + list(range(17, 19))  # 8-10 AM, 5-7 PM
        NIGHT_HOURS = list(range(22, 24)) + list(range(0, 6))

        for u, v, data in self.G.edges(data=True):
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

    def predict_eta_for_route(self, route, hour, is_monsoon, ambulance_type):
        """Use RF model to refine ETA prediction"""

        # Calculate route length
        route_length_km = 0
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            if self.G.has_edge(u, v):
                route_length_km += self.G[u][v].get('length_km', 1.0)

        # For now, since no RF model, use simple calculation
        # Placeholder: assume average speed 30 km/h
        eta_min = (route_length_km / 30) * 60

        return eta_min

    @staticmethod
    def _encode_ambulance_type(amb_type):
        """Encode ambulance type to number"""
        mapping = {'ALS': 3, 'BLS': 2, 'Mini': 1, 'Bike': 0}
        return mapping.get(amb_type, 0)