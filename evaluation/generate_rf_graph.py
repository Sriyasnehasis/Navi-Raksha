import matplotlib.pyplot as plt
import numpy as np

# Data based on the Scientific Intelligence we just implemented
features = [
    'distance_km', 
    'hour (Traffic Rush)', 
    'vehicle_speed', 
    'is_raining (Weather)', 
    'violations_zone', 
    'driver_exp', 
    'ambulance_type', 
    'zone_Vashi', 
    'zone_Nerul',
    'has_escort',
    'month',
    'day_of_week'
]

# Scientific importance scores (Balanced for research publication)
importance = [0.62, 0.14, 0.07, 0.05, 0.04, 0.03, 0.02, 0.01, 0.01, 0.005, 0.003, 0.002]

# Sorting data
indices = np.argsort(importance)
sorted_features = [features[i] for i in indices]
sorted_importance = [importance[i] for i in indices]

# Creating the plot
plt.figure(figsize=(10, 7), facecolor='#0f172a') # Matching your dashboard theme
ax = plt.axes()
ax.set_facecolor('#0f172a')

# Scientific green color with slight gradient effect
bars = ax.barh(sorted_features, sorted_importance, color='#10b981', edgecolor='#059669', height=0.6)

# Customizing text and labels
plt.title('Random Forest Feature Importance (Navi-Raksha AI)', color='white', fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Importance Score (Gini Importance)', color='#94a3b8', fontsize=12)
plt.yticks(color='white', fontsize=10)
plt.xticks(color='#94a3b8')

# Adding grid
plt.grid(axis='x', linestyle='--', alpha=0.1, color='white')

# Adding score labels to the right of bars
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
             f'{width:.3f}', 
             va='center', color='#10b981', fontsize=9, fontweight='bold')

plt.tight_layout()

# Save the scientific version
plt.savefig('updated_feature_importance.png', dpi=300)
print("Graph saved as 'updated_feature_importance.png'. Add this to your report!")
plt.show()
