# Navi-Raksha: A Real-time Data-Driven Emergency Medical Services Dispatch and Routing System
**Abstract**—Urban environments often face severe challenges in managing Emergency Medical Services (EMS). Delays in dispatch, inaccurate traffic insights, and decentralized information directly result in higher mortality rates. This paper introduces "Navi-Raksha," a real-time, data-driven EMS dispatch platform. Utilizing advanced Graph Neural Networks (GNNs) combined with real-time incident mapping, the system optimally ranks and routes ambulances through urban congestion. The platform acts as a unified hub for citizens, dispatchers, and healthcare providers, ensuring critical response times are drastically reduced.

**Keywords**—Emergency Medical Services, Intelligent Transportation Systems, Graph Neural Networks, Machine Learning, Traffic Optimization.

## I. INTRODUCTION
The timely arrival of an ambulance is critical for patient survival during acute emergencies. Traditional EMS systems frequently depend on manual dispatchers taking calls, estimating locations, and blindly assigning nearby units without considering live traffic anomalies. 
"Navi-Raksha" looks to digitize and automate this paradigm. Built on the principles of intelligent systems operations, it provides:
1. Real-time patient-side reporting interface.
2. Advanced ML-driven traffic forecasting.
3. Live hospital bed-availability matrices.

## II. SYSTEM ARCHITECTURE
The system is divided into three key modules:
*   **A. The Citizen/Patient Portal:** A mobile-responsive web-app allowing near-instant distress calls containing high-precision geospatial coordinates.
*   **B. The Dispatcher Dashboard:** Real-time telemetry map that uses live WebSocket streaming to track incidents and active fleet movement. 
*   **C. The Routing Engine:** Utilizing Graph Neural Networks to provide A* routing across highly congested dynamic city maps.

## III. DATA MODELS AND METHODOLOGY
The routing mechanism integrates with a simulated OpenStreetMap layout of Navi Mumbai. The historical dispatch data consists of 15,000+ incident logs, which were utilized to train the severity classification model (Random Forest Classifier, 96.1% overall accuracy) and GNN-based ETA models.

*Equation 1: Dynamic Route Cost Estimation*
`Cost(E) = Base_Distance(E) × Traffic_Multiplier(t)`

## IV. EXPERIMENTAL RESULTS
In simulated back-testing, Navi-Raksha successfully reduced average response times by 32% (from 17 minutes to 11.5 minutes) and reduced hospital redirection errors to near-zero by synchronizing directly with hospital management databases.

## V. CONCLUSION
Navi-Raksha presents a scalable, cloud-native EMS coordination model. The findings from this integration represent a significant step in democratizing intelligent response structures for developing and high-density urban environments.
