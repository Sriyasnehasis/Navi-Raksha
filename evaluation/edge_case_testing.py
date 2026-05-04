"""
ANJANAA (Navi-Raksha) - Edge Case Testing Suite
================================================
Uses REAL trained model from train_real.csv.
Tests edge cases based on actual dataset features.
Target: eta_minutes (regression)

Edge case categories:
  1. Extreme incident scenarios
  2. Network outages
  3. Low ambulance availability
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import json
import os
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
os.makedirs('outputs', exist_ok=True)

TRAIN_FILE = BASE_DIR / 'data' / 'processed' / 'train_real.csv'
TARGET = 'eta_minutes'
FEATURE_COLS = [
    'month', 'hour', 'day_of_week', 'is_weekend', 'is_monsoon',
    'is_raining', 'distance_km', 'vehicle_speed', 'violations_zone',
    'ambulance_type', 'has_escort', 'driver_exp',
    'zone_Vashi', 'zone_Nerul', 'zone_Kharghar', 'zone_Belapur', 'zone_Airoli'
]

# ETA thresholds (minutes) - based on dataset range 3-15 min
CRITICAL_ETA   = 12.0   # predicted ETA above this = concerning
SEVERE_ETA     = 14.0   # near max - critical failure

# ── LOAD & TRAIN ──────────────────────────────────────────
def build_model():
    print("  Loading train_real.csv and training RF model...")
    df = pd.read_csv(TRAIN_FILE)
    X  = df[FEATURE_COLS]
    y  = df[TARGET]
    model = RandomForestRegressor(n_estimators=200, max_depth=12,
                                  min_samples_leaf=2, random_state=42, n_jobs=-1)
    model.fit(X, y)
    print(f"  Model trained on {len(df)} real samples.")
    return model

# ── BASE ROW (normal scenario) ─────────────────────────────
def base_row():
    """Typical scenario: weekday afternoon, good conditions."""
    return {
        'month': 6, 'hour': 14, 'day_of_week': 2,
        'is_weekend': 0, 'is_monsoon': 0, 'is_raining': 0,
        'distance_km': 5.0, 'vehicle_speed': 40.0, 'violations_zone': 0,
        'ambulance_type': 1, 'has_escort': 0, 'driver_exp': 5,
        'zone_Vashi': 0, 'zone_Nerul': 1, 'zone_Kharghar': 0,
        'zone_Belapur': 0, 'zone_Airoli': 0,
    }

# ── EDGE CASE DEFINITIONS ─────────────────────────────────

# 1. EXTREME INCIDENT SCENARIOS
EXTREME_SCENARIOS = [
    {
        'name': 'Long Distance + Monsoon + Night',
        'description': 'Maximum distance during monsoon at midnight',
        'overrides': {'distance_km': 24.0, 'is_monsoon': 1, 'is_raining': 1,
                      'hour': 0, 'vehicle_speed': 15.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Maximum Distance + No Escort + Violations Zone',
        'description': 'Far call in a violations-heavy zone with no escort',
        'overrides': {'distance_km': 24.0, 'violations_zone': 1,
                      'has_escort': 0, 'vehicle_speed': 20.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Weekend Night Peak Hour',
        'description': 'Late night weekend call with rain',
        'overrides': {'is_weekend': 1, 'hour': 23, 'is_raining': 1,
                      'distance_km': 15.0, 'vehicle_speed': 25.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Storm Conditions + Inexperienced Driver',
        'description': 'Heavy rain, monsoon, new driver (exp=1)',
        'overrides': {'is_monsoon': 1, 'is_raining': 1,
                      'driver_exp': 1, 'vehicle_speed': 18.0,
                      'distance_km': 12.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Farthest Zone with All Adverse Conditions',
        'description': 'Airoli zone, max distance, monsoon, night, no escort',
        'overrides': {'zone_Vashi': 0, 'zone_Nerul': 0, 'zone_Kharghar': 0,
                      'zone_Belapur': 0, 'zone_Airoli': 1,
                      'distance_km': 24.0, 'is_monsoon': 1,
                      'hour': 2, 'has_escort': 0},
        'expected': 'HIGH_ETA',
    },
]

# 2. NETWORK OUTAGE SCENARIOS
# (In your dataset 'network_outage' isn't a column — we simulate it by
#  setting vehicle_speed to near 0 and violations_zone=1, which mimics
#  what happens operationally when comms/dispatch systems go down)
NETWORK_OUTAGE_SCENARIOS = [
    {
        'name': 'Network Outage — Low Severity Call',
        'description': 'Dispatch comms down (slow speed, violations) — routine call',
        'overrides': {'vehicle_speed': 5.0, 'violations_zone': 1,
                      'distance_km': 5.0},
        'expected': 'DEGRADED',
    },
    {
        'name': 'Network Outage — Critical Distance Call',
        'description': 'Dispatch down + long distance',
        'overrides': {'vehicle_speed': 5.0, 'violations_zone': 1,
                      'distance_km': 20.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Network Outage + Monsoon',
        'description': 'Combined comms failure and monsoon conditions',
        'overrides': {'vehicle_speed': 8.0, 'violations_zone': 1,
                      'is_monsoon': 1, 'is_raining': 1,
                      'distance_km': 12.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Partial Outage — Unknown Response Time',
        'description': 'Intermittent comms, near-zero speed reported',
        'overrides': {'vehicle_speed': 2.0, 'violations_zone': 1,
                      'distance_km': 8.0},
        'expected': 'DEGRADED',
    },
]

# 3. LOW AMBULANCE AVAILABILITY
# (ambulance_type=0 simulates an unavailable/non-standard unit;
#  has_escort=0 + driver_exp=1 simulates worst resource scenario)
LOW_AMBULANCE_SCENARIOS = [
    {
        'name': 'Non-Standard Ambulance — Long Distance',
        'description': 'Only basic/backup unit available for far call',
        'overrides': {'ambulance_type': 0, 'distance_km': 20.0,
                      'has_escort': 0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Backup Unit + Inexperienced Driver',
        'description': 'Worst resource combo: backup ambulance + new driver',
        'overrides': {'ambulance_type': 0, 'driver_exp': 1,
                      'has_escort': 0, 'distance_km': 15.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Backup Unit + Monsoon + Night',
        'description': 'Resource shortage during bad weather at night',
        'overrides': {'ambulance_type': 0, 'is_monsoon': 1,
                      'is_raining': 1, 'hour': 1,
                      'distance_km': 12.0},
        'expected': 'HIGH_ETA',
    },
    {
        'name': 'Combined Resource + Distance Shortage',
        'description': 'Backup unit, no escort, max distance, violations zone',
        'overrides': {'ambulance_type': 0, 'has_escort': 0,
                      'distance_km': 24.0, 'violations_zone': 1,
                      'driver_exp': 2},
        'expected': 'HIGH_ETA',
    },
]

# ── FAILURE RULES ─────────────────────────────────────────
def check_failures(pred_eta, scenario):
    failures = []
    exp = scenario.get('expected', '')

    if exp == 'HIGH_ETA' and pred_eta < CRITICAL_ETA:
        failures.append({
            'type':       'under_predicted_high_eta',
            'detail':     f'Expected HIGH ETA (>={CRITICAL_ETA} min) but model predicted {pred_eta:.2f} min.',
            'mitigation': (
                'Model underestimates ETA in this adverse scenario. '
                'Mitigation: Add a post-processing override — if distance_km > 18 '
                'AND (is_monsoon=1 OR vehicle_speed < 15), apply +3 min safety buffer. '
                'Retrain with augmented adverse-condition samples.'
            ),
        })

    if exp == 'DEGRADED' and pred_eta < 8.0:
        failures.append({
            'type':       'outage_eta_too_optimistic',
            'detail':     f'Network outage scenario predicted ETA of {pred_eta:.2f} min — too optimistic.',
            'mitigation': (
                'During comms degradation, assume worst-case routing delays. '
                'Mitigation: Flag vehicle_speed < 10 as a degraded-comms indicator '
                'and add minimum ETA floor of 10 min in dispatch logic.'
            ),
        })

    return failures

# ── RUN SCENARIOS ─────────────────────────────────────────
def run_scenario(model, scenario):
    row = base_row()
    row.update(scenario['overrides'])
    X = pd.DataFrame([row])[FEATURE_COLS]
    pred_eta = float(model.predict(X)[0])
    failures = check_failures(pred_eta, scenario)
    return {
        'scenario':    scenario['name'],
        'description': scenario['description'],
        'inputs':      scenario['overrides'],
        'predicted_eta_minutes': round(pred_eta, 4),
        'expected_severity':     scenario.get('expected', 'N/A'),
        'failures':              failures,
        'passed':                len(failures) == 0,
    }

def run_all(model):
    results = {'extreme': [], 'network_outage': [], 'low_ambulance': []}

    print("\n" + "="*55)
    print("  ANJANAA - Edge Case Testing Suite")
    print("  Using real RF model (train_real.csv)")
    print("="*55)

    for cat, scenarios in [
        ('extreme',       EXTREME_SCENARIOS),
        ('network_outage', NETWORK_OUTAGE_SCENARIOS),
        ('low_ambulance',  LOW_AMBULANCE_SCENARIOS),
    ]:
        print(f"\n{'─'*50}")
        print(f"  [{cat.replace('_',' ').title()}]")
        print(f"{'─'*50}")
        for sc in scenarios:
            r = run_scenario(model, sc)
            results[cat].append(r)
            status = "PASS" if r['passed'] else "FAIL"
            print(f"\n  [{status}]  {r['scenario']}")
            print(f"          {r['description']}")
            print(f"          Predicted ETA: {r['predicted_eta_minutes']:.2f} min  |  Expected: {r['expected_severity']}")
            if r['failures']:
                for f in r['failures']:
                    print(f"\n          FAILURE TYPE : {f['type']}")
                    print(f"          MITIGATION   : {f['mitigation']}")

    return results

# ── REPORT ────────────────────────────────────────────────
def generate_report(results):
    total  = sum(len(v) for v in results.values())
    passed = sum(r['passed'] for v in results.values() for r in v)
    failed = total - passed

    lines = [
        "=" * 60,
        "  ANJANAA (Navi-Raksha) - Edge Case Testing Report",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        f"\n  Total Tests : {total}",
        f"  Passed      : {passed}",
        f"  Failed      : {failed}",
        f"  Pass Rate   : {passed/total*100:.1f}%",
        "\n" + "-" * 60,
        "  FAILURES AND MITIGATIONS",
        "-" * 60,
    ]

    fc = 0
    for cat, tests in results.items():
        for t in tests:
            if not t['passed']:
                fc += 1
                lines.append(f"\n  [{fc}] {t['scenario']}")
                lines.append(f"      Category  : {cat.replace('_',' ').title()}")
                lines.append(f"      Predicted : {t['predicted_eta_minutes']} min")
                for f in t['failures']:
                    lines.append(f"      Failure   : {f['type']}")
                    lines.append(f"      Detail    : {f['detail']}")
                    lines.append(f"      Mitigation: {f['mitigation']}")

    if fc == 0:
        lines.append("\n  All edge case tests passed.")

    lines += [
        "\n" + "-" * 60,
        "  GENERAL MITIGATIONS FOR NAVI-RAKSHA",
        "-" * 60,
        "\n  1. Post-processing safety buffer: if distance > 18km AND",
        "     monsoon/rain conditions, add +3 min to predicted ETA.",
        "  2. Speed floor check: if vehicle_speed < 10, flag as",
        "     degraded-comms and apply minimum ETA floor of 10 min.",
        "  3. Confidence threshold: if prediction near 15 min (max),",
        "     escalate to human dispatcher for manual verification.",
        "  4. Retrain quarterly with new trip data including edge cases.",
        "  5. Monitor feature drift on distance_km and vehicle_speed.",
        "=" * 60,
    ]

    report_text = "\n".join(lines)

    with open('outputs/edge_case_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    print("\n  Saved: outputs/edge_case_report.txt")

    with open('outputs/edge_case_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print("  Saved: outputs/edge_case_results.json")

    return report_text

# ── MAIN ──────────────────────────────────────────────────
if __name__ == '__main__':
    model   = build_model()
    results = run_all(model)
    report  = generate_report(results)
    print("\n" + report)
    print("\nDone! Check evaluation/outputs/")
