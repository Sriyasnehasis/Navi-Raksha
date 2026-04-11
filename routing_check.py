import pickle
import pandas as pd
from modules.routing.dispatch_classifier import DispatchClassifier
from modules.routing.hospital_ranker import HospitalRanker
from modules.routing.a_star_router import AStarRouter
from modules.routing import NaviRakshaRouter

print('--- START CHECKLIST ---')
with open('data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
    G = pickle.load(f)
print('Load OSM graph ✓', 'nodes=', G.number_of_nodes(), 'edges=', G.number_of_edges())

locations_df = pd.read_csv('data/raw/key_locations.csv')
zone_to_node = {}
for idx, row in locations_df.iterrows():
    zone_name = row.get('Unnamed: 0', None) or row.get('zone_name', None)
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
print('Create zone-to-node mapping ✓', len(zone_to_node), 'zones')

node1 = zone_to_node.get('Vashi_CBD_Main') or next(iter(zone_to_node.values()))
node2 = zone_to_node.get('Belapur_Central') or (next(iter(zone_to_node.values())) if len(zone_to_node) > 1 else node1)
router = AStarRouter(G)
route, eta = router.find_route(node1, node2, hour=14, is_monsoon=False)
if route and eta < float('inf'):
    print('Find route between 2 zones ✓', 'path len=', len(route), 'eta=', eta)
else:
    raise RuntimeError('No route found')

eta_pred = router.predict_eta_for_route(route, 14, False, 'ALS')
print('ETA prediction on route ✓', 'eta_pred=', eta_pred)

dispatcher = DispatchClassifier()
assert dispatcher.classify('Critical', 5, 'Cardiac') == 'ALS'
assert dispatcher.classify('High', 10, 'Respiratory') == 'BLS'
assert dispatcher.classify('Medium', 1.0, 'Trauma') == 'Mini'
assert dispatcher.classify('Low', 1.0, 'Burn') == 'Bike'
print('Classify incident → ambulance type ✓')

hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
ranker = HospitalRanker(router, hospitals_df)
ranked = ranker.rank_hospitals(19.0822, 73.0308, ambulance_type='ALS', hour=14, is_monsoon=False)
assert isinstance(ranked, list) and len(ranked) <= 3 and len(ranked) > 0
print('Rank hospitals by ETA ✓', [(h['hospital_name'], h['eta_min']) for h in ranked])

routing = NaviRakshaRouter()
response = routing.handle_emergency({
    'patient_lat': 19.0822,
    'patient_lon': 73.0308,
    'incident_type': 'Cardiac',
    'severity': 'Critical',
    'hour': 14,
    'is_monsoon': False
})
assert 'ambulance_type' in response and 'best_hospital' in response
print('Full emergency flow test ✓', response)
print('--- END CHECKLIST ---')
