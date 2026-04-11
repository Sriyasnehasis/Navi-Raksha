import pickle
import pandas as pd
from modules.routing.a_star_router import AStarRouter

with open('data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
    G = pickle.load(f)

locations_df = pd.read_csv('data/raw/key_locations.csv')
zone_to_node = {}
for idx, row in locations_df.iterrows():
    zone_name = row['Unnamed: 0']
    lat = float(row['lat'])
    lon = float(row['lon'])
    min_dist = float('inf')
    nearest = None
    for node, attrs in G.nodes(data=True):
        d = ((attrs.get('y', 0) - lat) ** 2 + (attrs.get('x', 0) - lon) ** 2) ** 0.5
        if d < min_dist:
            min_dist = d
            nearest = node
    zone_to_node[zone_name] = nearest

hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
router = AStarRouter(G)
source_node = zone_to_node['Vashi_CBD_Main']
for idx, h in hospitals_df.iterrows():
    lat = float(h['lat'])
    lon = float(h['lon'])
    min_dist = float('inf')
    nearest = None
    for node, attrs in G.nodes(data=True):
        d = ((attrs.get('y', 0) - lat) ** 2 + (attrs.get('x', 0) - lon) ** 2) ** 0.5
        if d < min_dist:
            min_dist = d
            nearest = node
    route, eta = router.find_route(source_node, nearest, hour=14, is_monsoon=False)
    print(h['name'], 'node', nearest, 'route', route is not None, 'eta', eta)
