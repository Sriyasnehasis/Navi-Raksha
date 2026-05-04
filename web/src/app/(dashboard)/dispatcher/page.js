"use client";
export const dynamic = "force-dynamic";
import { useState, useEffect, useCallback } from "react";
import nextDynamic from "next/dynamic";
import { Bell, Activity, Shield, Zap, Info, Map as MapIcon, ChevronRight, AlertCircle, Clock, RefreshCw, Star, Users, Home, Phone } from "lucide-react";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

const LiveMap = nextDynamic(() => import("../../../components/LiveMap"), {
  ssr: false,
  loading: () => (
    <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", background: "#f1f5f9", color: "#94a3b8", fontFamily: "DM Sans, sans-serif", fontSize: 14 }}>
      Loading Intelligence Map…
    </div>
  ),
});

const INC_BORDER = { cardiac: "#DC2626", trauma: "#EA580C", respiratory: "#CA8A04", burn: "#9333EA", accident: "#EA580C", default: "#6B7280" };
const INC_PRIORITY = { critical: { label: "P1", bg: "#FEE2E2", color: "#DC2626" }, high: { label: "P2", bg: "#FFEDD5", color: "#EA580C" }, moderate: { label: "P3", bg: "#FEF9C3", color: "#CA8A04" }, low: { label: "P4", bg: "#F0FDF4", color: "#16A34A" } };

export default function AdminPanel() {
  const [ambulances, setAmbulances] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [isLive, setIsLive] = useState(false);
  const [dispatched, setDispatched] = useState({});
  const [showLogs, setShowLogs] = useState(null);
  const [reassigned, setReassigned] = useState({});

  const handleVerify = async (id) => {
    try {
      setDispatched(prev => ({ ...prev, [id]: true }));
      await fetch(`${BACKEND}/incidents/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Dispatched' })
      });
    } catch (err) {
      console.error("Dispatch Sync Failed:", err);
    }
  };

  const handleReassign = (id) => {
    const types = ["BLS — Basic Life Support", "First Responder Bike", "ALS — Advanced Life Support"];
    setReassigned(prev => {
      const current = prev[id] || 0;
      return { ...prev, [id]: (current + 1) % 3 };
    });
  };

  const handleCleanup = async () => {
    if (window.confirm("Purge all system data? This will delete all incidents and reset ambulances to clear Firebase quota.")) {
      try {
        const res = await fetch(`${BACKEND}/admin/cleanup`, { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
          alert("System Reset Complete");
          fetchData();
        }
      } catch (err) {
        alert("Cleanup Failed: " + err.message);
      }
    }
  };

  const fetchData = async () => {
    try {
      const [aR, iR, hR] = await Promise.all([
        fetch(`${BACKEND}/ambulances/active`),
        fetch(`${BACKEND}/incidents/active`),
        fetch(`${BACKEND}/hospitals`),
      ]);
      const newAmbs = (await aR.json()).ambulances || [];
      const newIncs = (await iR.json()).incidents || [];
      const newHosps = (await hR.json()).hospitals || [];

      setAmbulances(newAmbs);
      setIncidents(newIncs);
      setHospitals(newHosps);
      setIsLive(true);
    } catch {
      setIsLive(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    const initFetch = async () => { if (isMounted) await fetchData(); };
    initFetch();
    const t = setInterval(() => { if (isMounted) fetchData(); }, 4000);
    return () => { isMounted = false; clearInterval(t); };
  }, []);

  const avgEta = incidents.length > 0 
    ? (incidents.reduce((acc, inc) => acc + parseFloat(inc.prediction?.eta?.split(' ')[0] || 0), 0) / incidents.length).toFixed(1)
    : "0.0";

  const S = styles;

  return (
    <div style={S.root}>
      <div style={S.header}>
        <div style={S.headerLeft}>
           <h2 style={S.panelTitle}>Admin Intelligence Panel</h2>
           <div style={S.statusPill}><span style={S.statusDot} /> SYSTEM LIVE</div>
        </div>
        <div style={S.headerStats}>
           <div style={S.topStat}><div style={S.topStatVal}>{incidents.length}</div><div style={S.topStatLabel}>ACTIVE SOS</div></div>
           <div style={S.topStat}><div style={S.topStatVal}>{ambulances.filter(a=>a.status==='available').length}</div><div style={S.topStatLabel}>AVAIL UNITS</div></div>
           <div style={S.topStat}><div style={S.topStatVal}>{hospitals.length}</div><div style={S.topStatLabel}>HOSPITALS</div></div>
           <div style={S.topStat}><div style={S.topStatVal}>{avgEta}m</div><div style={S.topStatLabel}>AVG ETA</div></div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <button onClick={handleCleanup} style={{ background: '#FEF2F2', border: '1px solid #FEE2E2', borderRadius: '6px', padding: '4px 8px', fontSize: '11px', color: '#DC2626', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, fontWeight: 800 }}>
                <AlertCircle size={12} /> RESET GRID
              </button>
              <RefreshCw size={16} color="#94A3B8" style={{ cursor: 'pointer', animation: isLive ? 'spin 2s linear infinite' : 'none' }} onClick={fetchData} />
            </div>
        </div>
      </div>

      <div style={S.mainContent}>
        <div style={S.feedCol}>
           <div style={S.feedHeader}>
              <div style={S.feedTitle}><Zap size={18} fill="#EA580C" color="#EA580C" /> SOS Intelligence Feed</div>
              <div style={S.autoSync}>Updates every 5s</div>
           </div>
           <div style={S.feedScroll}>
              {incidents.map(inc => (
                <div key={inc.id} style={{ ...S.sosCard, borderLeft: `6px solid ${INC_BORDER[inc.incident_type?.toLowerCase()] || '#64748b'}`, background: dispatched[inc.id] ? '#F0FDF4' : '#fff', borderColor: dispatched[inc.id] ? '#16A34A' : '#E2E8F0' }}>
                   <div style={S.cardHeader}>
                      <div>
                        <span style={S.patientName}>{inc.patient_name}</span>
                        <span style={{ ...S.pBadge, background: (INC_PRIORITY[inc.severity?.toLowerCase()] || INC_PRIORITY.moderate).bg, color: (INC_PRIORITY[inc.severity?.toLowerCase()] || INC_PRIORITY.moderate).color }}>{(INC_PRIORITY[inc.severity?.toLowerCase()] || INC_PRIORITY.moderate).label}</span>
                        {inc.phone && <a href={`tel:${inc.phone}`} style={{ fontSize: 11, fontWeight: 700, color: '#4F46E5', marginTop: 4, display: 'flex', alignItems: 'center', gap: 6, textDecoration: 'none', cursor: 'pointer' }}><Phone size={12} /> {inc.phone}</a>}
                      </div>
                      <div style={S.timeSince}>
                        {inc.status === 'Resolved' ? (
                          <span style={{ color: '#16A34A', fontWeight: 800 }}>✅ RESOLVED</span>
                        ) : dispatched[inc.id] ? (
                          <span style={{ color: '#16A34A', fontWeight: 800 }}>DISPATCHED</span>
                        ) : (
                          <>{inc.time || '0:01'}</>
                        )}
                      </div>
                   </div>
                   <div style={S.cardSubtitle}>{inc.incident_type} · {inc.location_address || 'Navi Mumbai'}</div>
                   <div style={S.modelBox}>
                      <div style={S.modelHeader}><Shield size={10} /> RF MODEL RECOMMENDATION</div>
                      <div style={S.modelGrid}>
                         <div style={S.modelMain}>
                            <div style={S.modelLabel}>Ambulance Type</div>
                            <div style={S.modelVal}>{reassigned[inc.id] !== undefined ? ["BLS", "Bike", "ALS"][reassigned[inc.id]] : (inc.prediction?.type || "ALS")}</div>
                         </div>
                         <div style={S.modelSide}><div style={S.modelLabel}>ETA</div><div style={S.modelVal}>{inc.prediction?.eta || "4.0 min"}</div></div>
                      </div>
                      
                      {/* NEW: SCIENTIFIC FEATURE OUTPUT */}
                      {inc.prediction?.features_used && (
                        <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid #E2E8F0', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '4px 8px' }}>
                           <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>
                              TRAFFIC: <span style={{ color: '#475569' }}>{inc.prediction.features_used.hour >= 8 && inc.prediction.features_used.hour <= 10 ? 'HIGH' : 'STABLE'}</span>
                           </div>
                           <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>
                              WEATHER: <span style={{ color: '#475569' }}>{inc.prediction.features_used.is_raining ? '🌧️ RAIN' : '☀️ CLEAR'}</span>
                           </div>
                           <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>
                              DRIVER EXP: <span style={{ color: '#475569' }}>Lvl {inc.prediction.features_used.driver_exp}</span>
                           </div>
                           <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>
                              ZONE VIOL: <span style={{ color: '#475569' }}>{inc.prediction.features_used.violations_zone}</span>
                           </div>
                        </div>
                      )}
                   </div>
                   <div style={S.cardActions}>
                      <button style={{ ...S.dispatchBtn, background: dispatched[inc.id] ? '#16A34A' : '#1E3A8A' }} onClick={() => handleVerify(inc.id)}>{dispatched[inc.id] ? 'Unit Dispatched' : 'Verify & Dispatch'}</button>
                      <button style={S.secBtn} onClick={() => handleReassign(inc.id)}>Reassign</button>
                      <button style={S.secBtn} onClick={() => setShowLogs(inc)}>Logs</button>
                   </div>
                </div>
              ))}
           </div>
           {showLogs && (
              <div style={S.modalOverlay} onClick={() => setShowLogs(null)}>
                 <div style={S.modal} onClick={e => e.stopPropagation()}>
                    <div style={S.modalHeader}><h3>Log: {showLogs.patient_name}</h3><button onClick={() => setShowLogs(null)} style={S.closeBtn}>×</button></div>
                    <div style={S.modalBody}><div style={S.logItem}>Signal Received...</div></div>
                 </div>
              </div>
           )}
        </div>

        <div style={S.rightCol}>
           <div style={S.mapLegend}>
              <div style={S.legendLeft}><div><b>{ambulances.length}</b> ON MAP</div><div><b>{incidents.length}</b> INCIDENTS</div></div>
              <div style={S.legendRight}><div style={S.dotItem}><span style={{ ...S.dot, background: '#DC2626' }} /> ALS</div><div style={S.dotItem}><span style={{ ...S.dot, background: '#16A34A' }} /> Bike</div></div>
           </div>
           <div style={S.mapWrapper}>
              <LiveMap 
                userLat={incidents.length > 0 ? incidents[0].latitude : 19.076} 
                userLng={incidents.length > 0 ? incidents[0].longitude : 72.877} 
                ambulances={ambulances} 
                incidents={incidents} 
                hospitals={hospitals} 
              />
           </div>
           <div style={S.fleetSection}>
              <div style={S.fleetHeader}><div style={S.fleetTitle}><Activity size={16} /> Active Fleet</div></div>
              <div style={S.fleetGrid}>
                 {ambulances.map(amb => (
                   <div key={amb.id} style={S.fleetCard}>
                      <div style={S.fIcon}>🚑</div>
                      <div style={S.fInfo}>
                         <div style={S.fRow}><span style={S.fId}>{amb.id}</span><span style={{ ...S.fStatus, background: amb.status === 'available' ? '#DCFCE7' : '#FFEDD5', color: amb.status === 'available' ? '#16A34A' : '#EA580C' }}>{amb.status}</span></div>
                         <div style={S.fDriver}>{amb.driver_name}</div>
                      </div>
                   </div>
                 ))}
              </div>
           </div>
        </div>
      </div>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap'); body { margin: 0; background: #F8FAFC; } @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

const styles = {
  root: { minHeight: "100vh", display: "flex", flexDirection: "column", fontFamily: "'DM Sans', sans-serif", background: "#F8FAFC" },
  header: { background: "#fff", borderBottom: "1px solid #E2E8F0", padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", zIndex: 10, flexWrap: "wrap", gap: 16 },
  headerLeft: { display: "flex", alignItems: "center", gap: 16 },
  panelTitle: { fontSize: 18, fontWeight: 800, color: "#0F172A", margin: 0 },
  statusPill: { background: "#DCFCE7", color: "#16A34A", padding: "4px 10px", borderRadius: 40, fontSize: 9, fontWeight: 800, display: "flex", alignItems: "center", gap: 6 },
  statusDot: { width: 5, height: 5, borderRadius: "50%", background: "#16A34A" },
  headerStats: { display: "flex", alignItems: "center", gap: 20, flexWrap: "wrap" },
  topStat: { textAlign: "right" },
  topStatVal: { fontSize: 18, fontWeight: 800, color: "#0F172A", lineHeight: 1 },
  topStatLabel: { fontSize: 9, fontWeight: 700, color: "#94A3B8", marginTop: 2, textTransform: "uppercase" },
  mainContent: { flex: 1, display: "flex", flexWrap: "wrap", overflow: "hidden" },
  feedCol: { width: "100%", maxWidth: "440px", minWidth: "320px", background: "#fff", borderRight: "1px solid #E2E8F0", display: "flex", flexDirection: "column", height: "auto", flexGrow: 1 },
  feedHeader: { padding: "16px 20px 8px", display: "flex", justifyContent: "space-between", alignItems: "center" },
  feedTitle: { fontSize: 16, fontWeight: 800, color: "#0F172A", display: "flex", alignItems: "center", gap: 8 },
  autoSync: { fontSize: 10, color: "#3B82F6", fontWeight: 700 },
  feedScroll: { flex: 1, overflowY: "auto", padding: "12px 16px", display: "flex", flexDirection: "column", gap: 16, maxHeight: "600px" },
  sosCard: { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 20, padding: "16px", boxShadow: "0 4px 20px rgba(0,0,0,0.03)" },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 4 },
  patientName: { fontSize: 16, fontWeight: 800, color: "#0F172A" },
  pBadge: { marginLeft: 8, padding: "2px 6px", borderRadius: 4, fontSize: 9, fontWeight: 900 },
  timeSince: { fontSize: 9, color: "#94A3B8", textAlign: "right", fontWeight: 600 },
  cardSubtitle: { fontSize: 11, color: "#64748B", fontWeight: 600, marginBottom: 12 },
  modelBox: { background: "#F8FAFC", border: "1px solid #E2E8F0", borderRadius: 12, padding: "10px 14px", marginBottom: 12 },
  modelHeader: { fontSize: 8, fontWeight: 800, color: "#94A3B8", display: "flex", alignItems: "center", gap: 6, marginBottom: 6 },
  modelGrid: { display: "flex", gap: 12 },
  modelMain: { flex: 2 },
  modelSide: { flex: 1, borderLeft: "1px solid #E2E8F0", paddingLeft: 10 },
  modelLabel: { fontSize: 8, fontWeight: 700, color: "#94A3B8", marginBottom: 2 },
  modelVal: { fontSize: 10, fontWeight: 800, color: "#4F46E5", lineHeight: 1.2 },
  cardActions: { display: "flex", gap: 8 },
  dispatchBtn: { flex: 2, background: "#1E3A8A", color: "#fff", border: "none", padding: "8px", borderRadius: 8, fontWeight: 800, fontSize: 11, cursor: "pointer" },
  secBtn: { flex: 1, background: "#fff", border: "1px solid #E2E8F0", borderRadius: 8, fontWeight: 700, fontSize: 10, color: "#64748B", cursor: "pointer" },
  rightCol: { flex: 1, display: "flex", flexDirection: "column", minWidth: "320px", minHeight: "400px" },
  mapLegend: { padding: "10px 20px", background: "#fff", borderBottom: "1px solid #E2E8F0", display: "flex", justifyContent: "space-between", alignItems: "center" },
  legendLeft: { display: "flex", gap: 16, fontSize: 9, fontWeight: 700, color: "#64748B" },
  legendRight: { display: "flex", gap: 12, fontSize: 8, fontWeight: 800, color: "#94A3B8" },
  dotItem: { display: "flex", alignItems: "center", gap: 4 },
  dot: { width: 6, height: 6, borderRadius: "50%" },
  mapWrapper: { flex: 1, position: "relative", minHeight: "300px" },
  fleetSection: { padding: "16px 20px", background: "#fff", borderTop: "1px solid #E2E8F0" },
  fleetHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  fleetTitle: { fontSize: 12, fontWeight: 800, color: "#0F172A", display: "flex", alignItems: "center", gap: 8 },
  fleetGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 12 },
  fleetCard: { border: "1px solid #F1F5F9", borderRadius: 12, padding: "10px", display: "flex", gap: 10, background: "#F8FAFC" },
  fIcon: { fontSize: 16 },
  fInfo: { flex: 1 },
  fRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 },
  fId: { fontSize: 10, fontWeight: 800, color: "#0F172A" },
  fStatus: { fontSize: 7, fontWeight: 900, padding: "2px 4px", borderRadius: 3, textTransform: "uppercase" },
  fDriver: { fontSize: 9, fontWeight: 700, color: "#64748B" },
  modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(15, 23, 42, 0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000, backdropFilter: 'blur(4px)' },
  modal: { background: '#fff', width: "90%", maxWidth: "440px", borderRadius: 20, boxShadow: '0 20px 50px rgba(0,0,0,0.3)', padding: 24, position: 'relative' },
  modalHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, color: '#0F172A' },
  modalBody: { display: 'flex', flexDirection: 'column', gap: 10 },
  logItem: { fontSize: 12, color: '#64748B', padding: '10px', background: '#F8FAFC', borderRadius: 10, border: '1px solid #E2E8F0' },
  closeBtn: { background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', color: '#94A3B8' }
};
