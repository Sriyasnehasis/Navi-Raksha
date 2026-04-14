from modules.routing.a_star_router import AStarRouter
from modules.routing.dispatch_classifier import DispatchClassifier
from modules.routing.hospital_ranker import HospitalRanker

class NaviRakshaRouter:
    """Unified routing module"""

    def __init__(self):
        import pickle
        import pandas as pd
        import networkx as nx

        # Load graph
        with open('data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
            self.G = pickle.load(f)

        # Load models (placeholder)
        self.rf_model = None
        self.scaler = None

        # Load data
        self.hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
        self.locations_df = pd.read_csv('data/raw/key_locations.csv')

        # Initialize components
        self.router = AStarRouter(self.G, self.rf_model, self.scaler)
        self.dispatcher = DispatchClassifier()
        self.ranker = HospitalRanker(self.router, self.hospitals_df)

    def handle_emergency(self, incident_data):
        """
        Main function to handle an emergency call

        Input:
        {
            'patient_lat': 19.076,
            'patient_lon': 72.877,
            'incident_type': 'Cardiac',
            'severity': 'Critical',
            'hour': 14,
            'is_monsoon': False
        }

        Output:
        {
            'ambulance_type': 'ALS',
            'route': [...nodes...],
            'eta': 8.5,
            'hospitals': [
                {'name': 'Hospital A', 'eta': 12.3, 'beds': 5},
                {'name': 'Hospital B', 'eta': 15.1, 'beds': 3},
                {'name': 'Hospital C', 'eta': 18.2, 'beds': 1},
            ]
        }
        """

        # Step 1: Classify ambulance type
        ambulance_type = self.dispatcher.classify(
            incident_data['severity'],
            0,  # distance (unknown yet)
            incident_data['incident_type']
        )

        # Step 2: Rank hospitals
        ranked_hospitals = self.ranker.rank_hospitals(
            patient_lat=incident_data['patient_lat'],
            patient_lon=incident_data['patient_lon'],
            ambulance_type=ambulance_type,
            hour=incident_data['hour'],
            is_monsoon=incident_data['is_monsoon'],
            max_results=3
        )

        # Step 3: Find route to best hospital
        best_hospital = ranked_hospitals[0]
        route = best_hospital['route']

        return {
            'ambulance_type': ambulance_type,
            'route': route,
            'eta_min': best_hospital['eta_min'],
            'best_hospital': {
                'id': best_hospital['hospital_id'],
                'name': best_hospital['hospital_name'],
                'available_beds': best_hospital['available_beds'],
            },
            'alternatives': [
                {
                    'name': h['hospital_name'],
                    'eta_min': h['eta_min'],
                    'beds': h['available_beds']
                }
                for h in ranked_hospitals[1:]
            ]
        }

# Usage
if __name__ == "__main__":
    routing = NaviRakshaRouter()

    response = routing.handle_emergency({
        'patient_lat': 19.0822,  # Vashi
        'patient_lon': 73.0308,
        'incident_type': 'Cardiac',
        'severity': 'Critical',
        'hour': 14,
        'is_monsoon': False
    })

    print(f"Dispatch: {response['ambulance_type']}")
    print(f"ETA to hospital: {response['eta_min']:.1f} min")
    print(f"Best hospital: {response['best_hospital']['name']}")