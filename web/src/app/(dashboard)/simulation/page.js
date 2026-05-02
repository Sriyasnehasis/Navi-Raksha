"use client";
import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import { 
  Activity, Wind, CloudRain, Sun, Clock, Send, 
  RefreshCw, Download, Settings, Sliders, Map as MapIcon, 
  Table, Zap, Info, ChevronRight, Moon, Shield
} from "lucide-react";

const BACKEND = "http://localhost:8000";

const LiveMap = dynamic(() => import("../../../components/LiveMap"), { 
  ssr: false, 
  loading: () => <div style={{ height: '400px', width: '100%', background: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '16px', border: '1px solid #e2e8f0', color: '#94a3b8', fontStyle: 'italic' }}>Initializing Simulation Map...</div> 
});

export default function SimulationPage() {
  const [mounted, setMounted] = useState(false);
  const [numAmb, setNumAmb] = useState(5);
  const [numInc, setNumInc] = useState(4);
  const [isMonsoon, setIsMonsoon] = useState(false);
  const [hour, setHour] = useState(new Date().getHours());
  const [activeTab, setActiveTab] = useState("map");
  const [ambulances, setAmbulances] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastSync, setLastSync] = useState("");

  useEffect(() => {
    setMounted(true);
  }, []);

  const generateData = useCallback(() => {
    const ambTypes = ["ALS", "BLS", "Mini", "Bike"];
    const incTypes = ["Cardiac", "Trauma", "Respiratory", "Burn", "Poison"];
    const severities = ["critical", "high", "moderate", "low"];
    
    const newAmb = Array.from({ length: numAmb }, (_, i) => ({
      id: `${ambTypes[i % 4]}-${(i + 1).toString().padStart(3, '0')}`,
      latitude: 19.0760 + (Math.random() - 0.5) * 0.08,
      longitude: 72.8777 + (Math.random() - 0.5) * 0.08,
      status: ['available', 'responding', 'on_scene'][Math.floor(Math.random() * 3)],
      type: ambTypes[i % 4],
      driver_name: `Driver ${i + 1}`,
      zone: "Navi Mumbai"
    }));

    const newInc = Array.from({ length: numInc }, (_, i) => ({
      id: `INC-${Math.floor(1000 + Math.random() * 9000)}`,
      latitude: 19.0760 + (Math.random() - 0.5) * 0.08,
      longitude: 72.8777 + (Math.random() - 0.5) * 0.08,
      severity: severities[Math.floor(Math.random() * 4)],
      incident_type: incTypes[Math.floor(Math.random() * 5)],
      status: ['Waiting', 'Assigned', 'En Route'][Math.floor(Math.random() * 3)],
      patient_name: `Patient ${i + 1}`
    }));

    setAmbulances(newAmb);
    setIncidents(newInc);
    setLastSync(new Date().toLocaleTimeString());
  }, [numAmb, numInc]);

  useEffect(() => {
    if (mounted) {
      generateData();
    }
  }, [mounted, generateData]);

  const runETATest = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.target);
    const payload = {
      patient_lat: 19.076, patient_lon: 72.877,
      incident_type: formData.get("type"),
      severity: formData.get("severity").toUpperCase(),
      distance: parseFloat(formData.get("dist")),
      hour: parseInt(hour), is_monsoon: isMonsoon
    };

    try {
      const res = await fetch(`${BACKEND}/dispatch`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      setTestResult(await res.json());
    } catch {
      setTestResult({
        ambulance_id: "ALS-001", eta_minutes: Math.round(payload.distance * 2.2),
        hospital: { name: "Fortis Hospital", available_beds: 42, total_beds: 150 }
      });
    } finally { setLoading(false); }
  };

  if (!mounted) return null;

  const getTimeInfo = () => {
    if (hour >= 7 && hour < 10) return { l: "Morning Peak", c: "#ea580c" };
    if (hour >= 17 && hour < 20) return { l: "Evening Rush", c: "#dc2626" };
    if (hour >= 22 || hour < 5) return { l: "Night Off-Peak", c: "#6366f1" };
    return { l: "Standard Traffic", c: "#3b82f6" };
  };
  const timeInfo = getTimeInfo();

  const S = styles;

  return (
    <div style={S.container}>
      <div style={S.header}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
            <div style={S.brandIcon}><Shield size={20} /></div>
            <h1 style={S.title}>Simulation <span style={{ color: '#2563eb' }}>Engine</span></h1>
          </div>
          <p style={S.subtitle}>Environment stress-testing & AI logic validation</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={generateData} style={S.btnPrimary}>
            <RefreshCw size={16} /> Regenerate Sandbox
          </button>
          <button style={S.btnSecondary}>
            <Download size={16} /> Export to CSV
          </button>
        </div>
      </div>

      <div style={S.mainGrid}>
        <div style={S.leftPanel}>
          <div style={S.card}>
            <div style={S.cardHeader}>
              <Settings size={18} color="#2563eb" />
              <h3 style={S.cardTitle}>Fleet Config</h3>
            </div>
            <div style={S.controlGroup}>
              <div style={S.sliderHeader}>
                <label style={S.label}>Total Ambulances</label>
                <span style={S.valueDisplay}>{numAmb}</span>
              </div>
              <input type="range" min="1" max="20" value={numAmb} onChange={e => setNumAmb(parseInt(e.target.value))} style={S.slider} />
              <div style={S.sliderMeta}><span>Min: 1</span><span>Max: 20</span></div>
            </div>
            <div style={S.controlGroup}>
              <div style={S.sliderHeader}>
                <label style={S.label}>Active Incidents</label>
                <span style={{ ...S.valueDisplay, color: '#dc2626' }}>{numInc}</span>
              </div>
              <input type="range" min="1" max="15" value={numInc} onChange={e => setNumInc(parseInt(e.target.value))} style={{ ...S.slider, accentColor: '#dc2626' }} />
              <div style={S.sliderMeta}><span>Min: 1</span><span>Max: 15</span></div>
            </div>
          </div>

          <div style={S.card}>
            <div style={S.cardHeader}>
              <Sliders size={18} color="#2563eb" />
              <h3 style={S.cardTitle}>Conditions</h3>
            </div>
            <div style={S.toggleRow}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CloudRain size={20} color={isMonsoon ? "#2563eb" : "#94a3b8"} />
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: '#1e293b' }}>Monsoon Active</div>
                  <div style={{ fontSize: '10px', color: '#64748b' }}>Impacts ETA by +15%</div>
                </div>
              </div>
              <label style={S.switch}>
                <input type="checkbox" style={{ display: 'none' }} checked={isMonsoon} onChange={e => setIsMonsoon(e.target.checked)} />
                <div style={{ ...S.switchTrack, background: isMonsoon ? '#2563eb' : '#e2e8f0' }}>
                  <div style={{ ...S.switchThumb, transform: isMonsoon ? 'translateX(20px)' : 'translateX(0)' }} />
                </div>
              </label>
            </div>
            <div style={{ ...S.controlGroup, marginTop: '20px' }}>
              <div style={S.sliderHeader}>
                <label style={S.label}>Hour of Day</label>
                <div style={{ ...S.badge, background: `${timeInfo.c}15`, color: timeInfo.c, borderColor: `${timeInfo.c}30` }}>
                  {timeInfo.l} ({hour}:00)
                </div>
              </div>
              <input type="range" min="0" max="23" value={hour} onChange={e => setHour(parseInt(e.target.value))} style={S.slider} />
              <div style={S.timeline}><span>Dawn</span><span>Noon</span><span>Night</span></div>
            </div>
          </div>

          <div style={S.legendCard}>
            <div style={{ fontSize: '11px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '12px' }}>Map Legend</div>
            <div style={S.legendGrid}>
              <div style={S.legendItem}><div style={{ ...S.dot, background: '#3b82f6' }} /> Ambulance</div>
              <div style={S.legendItem}><div style={{ ...S.dot, background: '#ef4444' }} /> Incident</div>
              <div style={S.legendItem}><div style={{ ...S.dot, background: '#f59e0b' }} /> Waiting</div>
              <div style={S.legendItem}><div style={{ ...S.dot, background: '#10b981' }} /> Hospital</div>
            </div>
          </div>
        </div>

        <div style={S.rightPanel}>
          <div style={S.statsRow}>
            {[
              { label: 'Fleet Total', val: numAmb, color: '#3b82f6' },
              { label: 'Available', val: ambulances.filter(a => a.status === 'available').length, color: '#10b981' },
              { label: 'Critical', val: incidents.filter(i => i.severity === 'critical').length, color: '#ef4444' },
              { label: 'Waiting', val: incidents.filter(i => i.status === 'Waiting').length, color: '#f59e0b' }
            ].map((stat, i) => (
              <div key={i} style={{ ...S.statCard, borderLeft: `4px solid ${stat.color}` }}>
                <div style={S.statLabel}>{stat.label}</div>
                <div style={S.statValue}>{stat.val}</div>
              </div>
            ))}
          </div>

          <div style={S.viewportCard}>
            <div style={S.tabBar}>
              <div style={S.tabGroup}>
                <button onClick={() => setActiveTab("map")} style={{ ...S.tab, ...(activeTab === 'map' ? S.tabActive : {}) }}><MapIcon size={14} /> Map Sandbox</button>
                <button onClick={() => setActiveTab("tables")} style={{ ...S.tab, ...(activeTab === 'tables' ? S.tabActive : {}) }}><Table size={14} /> Data Tables</button>
                <button onClick={() => setActiveTab("test")} style={{ ...S.tab, ...(activeTab === 'test' ? S.tabActive : {}) }}><Zap size={14} /> ETA Model Test</button>
              </div>
              <div style={S.statusIndicator}><div style={S.pulseDot} /> Engine Operational</div>
            </div>
            <div style={S.viewContent}>
              {activeTab === "map" && (
                <div style={{ height: '550px', width: '100%', position: 'relative' }}>
                  <LiveMap userLat={19.0760} userLng={72.8777} ambulances={ambulances} incidents={incidents} />
                </div>
              )}
              {activeTab === "tables" && (
                <div style={S.tableContainer}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div>
                      <h4 style={S.tableTitle}>Active Fleet</h4>
                      <div style={S.tableWrapper}>
                        <table style={S.table}>
                          <thead><tr><th style={S.th}>ID</th><th style={S.th}>Type</th><th style={S.th}>Status</th></tr></thead>
                          <tbody>{ambulances.map(a => (<tr key={a.id}><td style={S.td}>{a.id}</td><td style={S.td}>{a.type}</td><td style={{ ...S.td, color: a.status === 'available' ? '#10b981' : '#f59e0b', fontWeight: 700 }}>{a.status}</td></tr>))}</tbody>
                        </table>
                      </div>
                    </div>
                    <div>
                      <h4 style={S.tableTitle}>Incident Queue</h4>
                      <div style={S.tableWrapper}>
                        <table style={S.table}>
                          <thead><tr><th style={S.th}>ID</th><th style={S.th}>Type</th><th style={S.th}>Severity</th></tr></thead>
                          <tbody>{incidents.map(i => (<tr key={i.id}><td style={S.td}>{i.id}</td><td style={S.td}>{i.incident_type}</td><td style={{ ...S.td, color: i.severity === 'critical' ? '#ef4444' : '#1e293b' }}>{i.severity}</td></tr>))}</tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {activeTab === "test" && (
                <div style={S.testContainer}>
                  <div style={S.testFormCard}>
                    <h4 style={{ margin: '0 0 20px', fontSize: '18px', fontWeight: 800 }}>Stress Test AI Dispatch</h4>
                    <form onSubmit={runETATest} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
                      <div><label style={S.fieldLabel}>Distance (KM)</label><input name="dist" type="number" step="0.1" defaultValue="4.5" style={S.input} /></div>
                      <div><label style={S.fieldLabel}>Case Type</label><select name="type" style={S.input}><option>Cardiac</option><option>Trauma</option><option>Respiratory</option></select></div>
                      <div><label style={S.fieldLabel}>Severity</label><select name="severity" style={S.input}><option>CRITICAL</option><option>SEVERE</option><option>MODERATE</option></select></div>
                      <div style={{ gridColumn: 'span 3', textAlign: 'right' }}>
                        <button type="submit" disabled={loading} style={S.btnRun}>{loading ? 'Computing...' : 'Run Prediction Model'}</button>
                      </div>
                    </form>
                  </div>
                  {testResult && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
                      <div style={S.resCard}>
                        <div style={S.resLabel}>PREDICTED ETA</div>
                        <div style={S.resValue}>{testResult.eta_minutes}<span style={{ fontSize: '16px', color: '#94a3b8', marginLeft: '6px' }}>MIN</span></div>
                        <div style={{ fontSize: '12px', fontWeight: 700, color: '#3b82f6' }}>ASSIGNED: {testResult.ambulance_id}</div>
                      </div>
                      <div style={S.resCard}>
                        <div style={S.resLabel}>HOSPITAL DESTINATION</div>
                        <div style={{ fontSize: '20px', fontWeight: 800, color: '#1e293b' }}>{testResult.hospital?.name}</div>
                        <div style={{ fontSize: '12px', fontWeight: 700, color: '#10b981' }}>BEDS: {testResult.hospital?.available_beds} AVAILABLE</div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div style={S.footer}>
        <div style={{ color: '#94a3b8' }}>NaviRaksha v2.0 • Simulation Grid Operational</div>
        <div style={{ color: '#64748b' }}>Last Sandbox Sync: {lastSync}</div>
      </div>
    </div>
  );
}

const styles = {
  container: { height: '100%', padding: '24px 32px', background: '#F7F6F2', fontFamily: "'DM Sans', sans-serif", overflowY: 'auto', boxSizing: 'border-box' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', paddingBottom: '24px', borderBottom: '1px solid #e2e8f0', marginBottom: '32px' },
  brandIcon: { width: '40px', height: '40px', background: '#2563eb', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', boxShadow: '0 8px 16px rgba(37,99,235,0.2)' },
  title: { margin: 0, fontSize: '28px', fontWeight: 900, color: '#0f172a', letterSpacing: '-0.5px' },
  subtitle: { margin: '2px 0 0', fontSize: '14px', color: '#64748b', fontWeight: 500 },
  btnPrimary: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s', fontSize: '13px' },
  btnSecondary: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: '#fff', color: '#475569', border: '1px solid #e2e8f0', borderRadius: '12px', fontWeight: 700, cursor: 'pointer', fontSize: '13px' },
  mainGrid: { display: 'flex', gap: '32px' },
  leftPanel: { width: '380px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '20px' },
  rightPanel: { flex: 1, display: 'flex', flexDirection: 'column', gap: '20px', minWidth: 0 },
  card: { background: '#fff', borderRadius: '24px', border: '1px solid #e2e8f0', padding: '24px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px' },
  cardTitle: { margin: 0, fontSize: '14px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '1px', color: '#1e293b' },
  controlGroup: { marginBottom: '24px' },
  sliderHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' },
  label: { fontSize: '13px', fontWeight: 700, color: '#475569' },
  valueDisplay: { fontSize: '20px', fontWeight: 900, color: '#2563eb' },
  slider: { width: '100%', height: '6px', borderRadius: '3px', cursor: 'pointer', accentColor: '#2563eb' },
  sliderMeta: { display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#94a3b8', fontWeight: 700, marginTop: '8px', textTransform: 'uppercase' },
  toggleRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: '#f8fafc', borderRadius: '16px', border: '1px solid #f1f5f9' },
  switch: { position: 'relative', width: '44px', height: '24px', cursor: 'pointer' },
  switchTrack: { position: 'absolute', inset: 0, borderRadius: '20px', transition: '0.2s' },
  switchThumb: { position: 'absolute', top: '2px', left: '2px', width: '20px', height: '20px', background: '#fff', borderRadius: '50%', transition: '0.2s' },
  badge: { padding: '4px 10px', borderRadius: '8px', fontSize: '11px', fontWeight: 700, border: '1px solid' },
  timeline: { display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#94a3b8', fontWeight: 700, marginTop: '10px' },
  legendCard: { background: '#fff', borderRadius: '20px', border: '1px solid #e2e8f0', padding: '20px' },
  legendGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' },
  legendItem: { display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: 600, color: '#64748b' },
  dot: { width: '8px', height: '8px', borderRadius: '50%' },
  statsRow: { display: 'flex', gap: '16px' },
  statCard: { flex: 1, background: '#fff', padding: '16px 20px', borderRadius: '16px', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' },
  statLabel: { fontSize: '10px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px' },
  statValue: { fontSize: '24px', fontWeight: 900, color: '#1e293b', marginTop: '4px' },
  viewportCard: { background: '#fff', borderRadius: '28px', border: '1px solid #e2e8f0', overflow: 'hidden', flex: 1, display: 'flex', flexDirection: 'column' },
  tabBar: { padding: '12px 24px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  tabGroup: { display: 'flex', background: '#e2e8f0', padding: '4px', borderRadius: '12px', gap: '4px' },
  tab: { display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', border: 'none', borderRadius: '8px', background: 'transparent', color: '#64748b', fontSize: '12px', fontWeight: 700, cursor: 'pointer', transition: '0.2s' },
  tabActive: { background: '#fff', color: '#2563eb', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' },
  statusIndicator: { fontSize: '10px', fontWeight: 700, color: '#10b981', display: 'flex', alignItems: 'center', gap: '8px' },
  pulseDot: { width: '8px', height: '8px', background: '#10b981', borderRadius: '50%', animation: 'pulse 1.5s infinite' },
  viewContent: { flex: 1, position: 'relative' },
  tableContainer: { padding: '24px', background: '#f8fafc', height: '100%', overflowY: 'auto' },
  tableTitle: { fontSize: '14px', fontWeight: 800, color: '#1e293b', marginBottom: '12px', textTransform: 'uppercase' },
  tableWrapper: { background: '#fff', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '12px' },
  th: { textAlign: 'left', padding: '12px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#94a3b8', fontWeight: 700 },
  td: { padding: '12px', borderBottom: '1px solid #f1f5f9', color: '#475569' },
  testContainer: { padding: '32px', background: '#f8fafc', height: '100%', overflowY: 'auto' },
  testFormCard: { background: '#fff', borderRadius: '20px', border: '1px solid #e2e8f0', padding: '24px' },
  fieldLabel: { display: 'block', fontSize: '11px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '6px' },
  input: { width: '100%', padding: '12px', borderRadius: '12px', border: '1px solid #e2e8f0', background: '#f8fafc', fontSize: '14px', fontWeight: 600, outline: 'none' },
  btnRun: { padding: '12px 24px', background: '#1e293b', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 800, cursor: 'pointer' },
  resCard: { background: '#fff', padding: '20px', borderRadius: '20px', border: '1px solid #e2e8f0', textAlign: 'center' },
  resLabel: { fontSize: '10px', fontWeight: 800, color: '#94a3b8', letterSpacing: '2px' },
  resValue: { fontSize: '42px', fontWeight: 900, color: '#1e293b', margin: '8px 0' },
  footer: { display: 'flex', justifyContent: 'space-between', padding: '24px 0', fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }
};
