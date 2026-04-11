import pickle
import pandas as pd
from modules.routing.a_star_router import AStarRouter
from modules.routing.hospital_ranker import HospitalRanker

with open('data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
    G = pickle.load(f)

hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
router = AStarRouter(G)
ranker = HospitalRanker(router, hospitals_df)

print('hospital rows', len(hospitals_df))
print(hospitals_df.head())

hospitals = ranker.rank_hospitals(19.076, 72.877)
print('ranked count', len(hospitals))
print('hospitals', hospitals)
