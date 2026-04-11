import pickle
import pandas as pd
from modules.routing.a_star_router import AStarRouter
from modules.routing.dispatch_classifier import DispatchClassifier
from modules.routing.hospital_ranker import HospitalRanker

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

print('Has Vashi exact key?', 'Vashi' in zone_to_node)
print('Has CBD_Main exact key?', 'CBD_Main' in zone_to_node)
print('Has Vashi_CBD_Main?', 'Vashi_CBD_Main' in zone_to_node)

node1 = zone_to_node['Vashi_CBD_Main']
node2 = zone_to_node.get('Belapur_Central')
router = AStarRouter(G)
route, eta = router.find_route(node1, node2, hour=17, is_monsoon=False)
print('Test 1 route exists:', route is not None)
print('Test 1 eta:', eta)
print('Test 1 eta < 20:', eta < 20)

classifier = DispatchClassifier()
amb_type = classifier.classify('Critical', 5, 'Cardiac')
print('Test 2 amb_type:', amb_type)
print('Test 2 pass:', amb_type == 'ALS')

hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
ranker = HospitalRanker(router, hospitals_df)
hospitals = ranker.rank_hospitals(19.076, 72.877)
print('Test 3 count:', len(hospitals))
if len(hospitals) >= 2:
    print('Test 3 sorted by eta:', hospitals[0]['eta_min'] <= hospitals[1]['eta_min'])
print('Top hospitals:', [(h['hospital_name'], h['eta_min']) for h in hospitals])
