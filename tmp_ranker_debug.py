import pickle
import pandas as pd
from modules.routing.a_star_router import AStarRouter
from modules.routing.hospital_ranker import HospitalRanker

with open('data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
    G = pickle.load(f)

hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
router = AStarRouter(G)
ranker = HospitalRanker(router, hospitals_df)

patient_node = ranker._find_nearest_node(19.076, 72.877)
print('patient_node', patient_node)
for idx, hospital in hospitals_df.iterrows():
    hospital_node = ranker._get_hospital_node(hospital['id'])
    route, eta = router.find_route(source_node=patient_node, dest_node=hospital_node, hour=14, is_monsoon=False)
    print('hospital', hospital['name'], 'hospital_node', hospital_node, 'route_exists', route is not None, 'len', len(route) if route else 0, 'eta', eta)
    print('hospital route type', type(route), route[:3])
    print('---')
