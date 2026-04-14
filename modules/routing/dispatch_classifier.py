class DispatchClassifier:
    """Classify incident severity → ambulance type"""

    @staticmethod
    def classify(incident_severity, distance_km, incident_type):
        """
        Args:
            incident_severity: 'Critical', 'High', 'Medium', 'Low'
            distance_km: Distance to incident
            incident_type: 'Cardiac', 'Trauma', 'Respiratory', 'Burn', etc.

        Returns:
            'ALS', 'BLS', 'Mini', 'Bike'
        """

        # Critical = Advance Life Support (ALS)
        if incident_severity == 'Critical':
            return 'ALS'

        # High = Basic Life Support
        if incident_severity == 'High':
            if incident_type in ['Cardiac', 'Trauma', 'Burn']:
                return 'ALS'
            return 'BLS'

        # Medium = Based on distance
        if incident_severity == 'Medium':
            if distance_km < 2:
                return 'Mini'  # Close, fast response
            return 'BLS'

        # Low = Motorcycle
        if incident_severity == 'Low':
            return 'Bike'  # Quick first assessment

        return 'BLS'  # Default

    @staticmethod
    def get_availability_of_type(ambulance_type, ambulances_db):
        """Check how many ambulances of this type are available"""
        count = 0
        for amb in ambulances_db:
            if amb['type'] == ambulance_type and amb['status'] == 'Available':
                count += 1
        return count

# Usage
if __name__ == "__main__":
    dispatcher = DispatchClassifier()

    dispatch_type = dispatcher.classify(
        incident_severity='Critical',
        distance_km=5.2,
        incident_type='Cardiac'
    )
    print(f"Dispatch: {dispatch_type}")  # Output: 'ALS'