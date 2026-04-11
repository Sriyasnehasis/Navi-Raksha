import pandas as pd
import numpy as np

class HospitalRanker:
    """Rank hospitals by ETA and availability"""

    def __init__(self, router, hospitals_df):
        """
        Args:
            router: AStarRouter instance
            hospitals_df: DataFrame with columns [id, name, lat, lon, beds, available_beds]
        """
        self.router = router
        self.hospitals_df = hospitals_df

    def rank_hospitals(self, patient_lat, patient_lon, ambulance_type='ALS', hour=12, is_monsoon=False, max_results=3):
        """
        Rank hospitals by ETA

        Returns:
            List of hospitals sorted by ETA (best first)
        """

        # Find nearest hospital node to patient location
        patient_node = self._find_nearest_node(patient_lat, patient_lon)

        hospital_rankings = []

        for idx, hospital in self.hospitals_df.iterrows():
            # Find route from patient to hospital
            hospital_node = self._get_hospital_node(hospital['id'])

            route, travel_time = self.router.find_route(
                source_node=patient_node,
                dest_node=hospital_node,
                hour=hour,
                is_monsoon=is_monsoon
            )

            if route is None:
                continue

            # Predict ETA using RF model (placeholder for now)
            eta_min = travel_time  # For now, use travel_time as ETA

            # Score: balance ETA + bed availability
            bed_availability_ratio = hospital['available_beds'] / hospital['beds']

            # Weighted score: 70% ETA, 30% beds
            score = (0.7 * eta_min) + (0.3 * (1 - bed_availability_ratio) * 30)

            hospital_rankings.append({
                'rank': len(hospital_rankings) + 1,
                'hospital_id': hospital['id'],
                'hospital_name': hospital['name'],
                'eta_min': eta_min,
                'available_beds': hospital['available_beds'],
                'total_beds': hospital['beds'],
                'bed_availability': f"{bed_availability_ratio*100:.1f}%",
                'score': score,
                'route': route,
            })

        # Sort by score (lower is better)
        hospital_rankings.sort(key=lambda x: x['score'])

        return hospital_rankings[:max_results]

    def _find_nearest_node(self, lat, lon):
        """Find nearest graph node to given coordinates"""
        min_dist = float('inf')
        nearest_node = None

        for node, attrs in self.router.G.nodes(data=True):
            node_lat = attrs.get('y', 0)
            node_lon = attrs.get('x', 0)

            dist = ((node_lat - lat)**2 + (node_lon - lon)**2)**0.5

            if dist < min_dist:
                min_dist = dist
                nearest_node = node

        return nearest_node

    def _get_hospital_node(self, hospital_id):
        """Get OSM node ID for hospital"""
        # This should be in your hospitals_df or cached
        # For now, find nearest node to hospital coordinates
        hospital = self.hospitals_df[self.hospitals_df['id'] == hospital_id].iloc[0]
        return self._find_nearest_node(hospital['lat'], hospital['lon'])

# Test
if __name__ == "__main__":
    # Dummy router for testing
    class DummyRouter:
        def __init__(self):
            import pickle
            with open("data/raw/navi_mumbai_road_graph.pkl", "rb") as f:
                self.G = pickle.load(f)

        def find_route(self, source_node, dest_node, hour, is_monsoon):
            # Dummy: return random route and time
            return [source_node, dest_node], 10.0

    hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
    router = DummyRouter()
    ranker = HospitalRanker(router, hospitals_df)

    # Get ranked hospitals
    ranked = ranker.rank_hospitals(
        patient_lat=19.076,
        patient_lon=72.877,
        ambulance_type='ALS',
        hour=14,
        is_monsoon=False,
        max_results=3
    )

    print("Top 3 Hospitals:")
    for h in ranked:
        print(f"  {h['rank']}. {h['hospital_name']} - ETA: {h['eta_min']:.1f} min, Beds: {h['available_beds']}/{h['total_beds']}")