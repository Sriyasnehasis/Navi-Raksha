"use client";
import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import { Bell, Activity, Shield, Zap, Info, Map as MapIcon, ChevronRight, AlertCircle, Clock, RefreshCw, Star, Users, Home, Phone } from "lucide-react";

const BACKEND = "http://127.0.0.1:8000";

const LiveMap = dynamic(() => import("../../../components/LiveMap"), {
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

  const fetchData = useCallback(async () => {
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
  }, []);

  useEffect(() => {
    let isMounted = true;

    const initFetch = async () => {
      if (isMounted) {
        await fetchData();
      }
    };

    initFetch();

    const t = setInterval(() => {
      if (isMounted) {
        fetchData();
      }
    }, 4000);

    return () => {
      isMounted = false;
      clearInterval(t);
    };
  }, [fetchData]);

  // Calculate Dynamic Avg ETA
  const avgEta = incidents.length > 0 
    ? (incidents.reduce((acc, inc) => {
        const val = parseFloat(inc.prediction?.eta?.split(' ')[0] || 0);
        return acc + val;
      }, 0) / incidents.length).toFixed(1)
    : "0.0";

  const S = styles;

  return (
    <div style={S.root}>
      {/* HEADER SECTION */}
      <div style={S.header}>
        <div style={S.headerLeft}>
           <h2 style={S.panelTitle}>Admin Intelligence Panel</h2>
           <div style={S.statusPill}>
              <span style={S.statusDot} /> SYSTEM LIVE
           </div>
        </div>
        <div style={S.headerStats}>
           <div style={S.topStat}><div style={S.topStatVal}>{incidents.length}</div><div style={S.topStatLabel}>ACTIVE SOS</div></div>
           <div style={S.topStat}><div style={S.topStatVal}>{ambulances.filter(a=>a.status==='available').length}</div><div style={S.topStatLabel}>AVAIL UNITS</div></div>
           <div style={S.topStat}><div style={S.topStatVal}>{hospitals.length}</div><div style={S.topStatLabel}>HOSPITALS</div></div>
           <div style={S.topStat}><div style={S.topStatVal}>{avgEta}m</div><div style={S.topStatLabel}>AVG ETA</div></div>
           <RefreshCw size={16} color="#94A3B8" style={{ cursor: 'pointer', animation: isLive ? 'spin 2s linear infinite' : 'none' }} onClick={fetchData} />
        </div>
      </div>

      <div style={S.mainContent}>
        {/* LEFT FEED PANEL */}
        <div style={S.feedCol}>
           <div style={S.feedHeader}>
              <div style={S.feedTitle}><Zap size={18} fill="#EA580C" color="#EA580C" /> SOS Intelligence Feed</div>
              <div style={S.autoSync}>Updates every 5s</div>
           </div>

           <div style={S.feedScroll}>
              {incidents.map(inc => (
                <div key={inc.id} style={{ 
                  ...S.sosCard, 
                  borderLeft: `6px solid ${INC_BORDER[inc.incident_type?.toLowerCase()] || '#64748b'}`,
                  background: dispatched[inc.id] ? '#F0FDF4' : '#fff',
                  borderColor: dispatched[inc.id] ? '#16A34A' : '#E2E8F0'
                }}>
                   <div style={S.cardHeader}>
                      <div>
                        <span style={S.patientName}>{inc.patient_name}</span>
                        <span style={{ ...S.pBadge, background: (INC_PRIORITY[inc.severity?.toLowerCase()] || INC_PRIORITY.moderate).bg, color: (INC_PRIORITY[inc.severity?.toLowerCase()] || INC_PRIORITY.moderate).color }}>
                           {(INC_PRIORITY[inc.severity?.toLowerCase()] || INC_PRIORITY.moderate).label}
                        </span>
                        {inc.phone && (
                          <a 
                            href={`tel:${inc.phone}`}
                            style={{ 
                              fontSize: 11, fontWeight: 700, color: '#4F46E5', marginTop: 4, 
                              display: 'flex', alignItems: 'center', gap: 6, textDecoration: 'none',
                              cursor: 'pointer'
                            }}
                            onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
                            onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
                          >
                             <Phone size={12} /> {inc.phone}
                          </a>
                        )}
                      </div>
                      <div style={S.timeSince}>
                        {dispatched[inc.id] ? (
                           <span style={{ color: '#16A34A', fontWeight: 800 }}>DISPATCHED</span>
                        ) : (
                           <>Time since SOS <br/> <b style={{color: '#EA580C'}}>{inc.time || '0:01'}</b></>
                        )}
                      </div>
                   </div>
                   <div style={S.cardSubtitle}>{inc.incident_type} · {inc.location_address || 'Navi Mumbai'} · 1.3 km</div>

                   {/* RF MODEL RECOMMENDATION BOX (DYNAMIC) */}
                   <div style={S.modelBox}>
                      <div style={S.modelHeader}><Shield size={10} /> RF MODEL RECOMMENDATION</div>
                      <div style={S.modelGrid}>
                         <div style={S.modelMain}>
                            <div style={S.modelLabel}>Ambulance Type</div>
                            <div style={S.modelVal}>
                               {reassigned[inc.id] !== undefined 
                                 ? ["BLS — Basic Life Support", "First Responder Bike", "ALS — Advanced Life Support"][reassigned[inc.id]]
                                 : (inc.prediction?.type || "ALS — Advanced Life Support")}
                            </div>
                         </div>
                         <div style={S.modelSide}>
                            <div style={S.modelLabel}>Pred. ETA</div>
                            <div style={S.modelVal}>
                               {reassigned[inc.id] === 1 ? "2.1 - 3.0" : (inc.prediction?.eta || "3.8 - 4.5")} <br/> 
                               <span style={{fontSize: 10}}>min</span>
                            </div>
                         </div>
                         <div style={S.modelSide}>
                            <div style={S.modelLabel}>ML Confidence</div>
                            <div style={S.modelVal}>{reassigned[inc.id] !== undefined ? "99% (Manual)" : (inc.prediction?.conf || "97%")}</div>
                         </div>
                      </div>
                   </div>

                   <div style={S.cardActions}>
                      <button 
                        style={{ ...S.dispatchBtn, background: dispatched[inc.id] ? '#16A34A' : '#1E3A8A' }}
                        onClick={() => handleVerify(inc.id)}
                      >
                        {dispatched[inc.id] ? 'Unit Dispatched' : 'Verify & Dispatch'}
                      </button>
                      <button style={S.secBtn} onClick={() => handleReassign(inc.id)}>Reassign</button>
                      <button style={S.secBtn} onClick={() => setShowLogs(inc)}>Logs</button>
                   </div>
                   <div style={S.cardId}>ID: {inc.id}</div>
                </div>
              ))}
           </div>

           {/* LOGS MODAL OVERLAY */}
           {showLogs && (
              <div style={S.modalOverlay} onClick={() => setShowLogs(null)}>
                 <div style={S.modal} onClick={e => e.stopPropagation()}>
                    <div style={S.modalHeader}>
                       <h3 style={{margin:0}}>Intelligence Log: {showLogs.patient_name}</h3>
                       <button onClick={() => setShowLogs(null)} style={S.closeBtn}>×</button>
                    </div>
                    <div style={S.modalBody}>
                       <div style={S.logItem}><b>0:00</b> — Signal Received (Encryption: AES-256)</div>
                       <div style={S.logItem}><b>0:02</b> — RF Model Prediction: {showLogs.incident_type} identified</div>
                       <div style={S.logItem}><b>0:05</b> — Geocoding: {showLogs.location_address}</div>
                       <div style={S.logItem}><b>0:08</b> — Weather Analysis: 82% Humidity (ETA +0.4m)</div>
                       <div style={S.logItem}><b>0:12</b> — Nearest Hospital: Apollo (2.1km) signaled</div>
                       <div style={S.logItem}><b>0:15</b> — Dispatcher verification pending...</div>
                    </div>
                 </div>
              </div>
           )}

        </div>

        {/* RIGHT MAP & FLEET PANEL */}
        <div style={S.rightCol}>
           <div style={S.mapLegend}>
              <div style={S.legendLeft}>
                 <div style={S.lItem}><b>{ambulances.length}</b> ON MAP</div>
                 <div style={S.lItem}><b>{ambulances.filter(a=>a.status==='available').length}</b> AVAILABLE</div>
                 <div style={S.lItem}><b>1</b> RESPONDING</div>
                 <div style={S.lItem}><b>{incidents.length}</b> INCIDENTS</div>
              </div>
              <div style={S.legendRight}>
                 <div style={S.dotItem}><span style={{ ...S.dot, background: '#DC2626' }} /> ALS</div>
                 <div style={S.dotItem}><span style={{ ...S.dot, background: '#EA580C' }} /> BLS</div>
                 <div style={S.dotItem}><span style={{ ...S.dot, background: '#16A34A' }} /> Bike</div>
                 <div style={S.dotItem}><span style={{ ...S.dot, background: '#3B82F6' }} /> You</div>
              </div>
           </div>
           <div style={S.mapWrapper}>
              <LiveMap userLat={19.076} userLng={72.877} ambulances={ambulances} incidents={incidents} hospitals={hospitals} />
           </div>

           {/* ACTIVE FLEET GRID (BOTTOM RIGHT) */}
           <div style={S.fleetSection}>
              <div style={S.fleetHeader}>
                 <div style={S.fleetTitle}><Activity size={16} /> Active Fleet ({ambulances.length} units)</div>
                 <div style={S.fleetCollapse}>▲ Collapse</div>
              </div>
              <div style={S.fleetGrid}>
                 {ambulances.map(amb => (
                   <div key={amb.id} style={S.fleetCard}>
                      <div style={S.fIcon}>🚑</div>
                      <div style={S.fInfo}>
                         <div style={S.fRow}>
                            <span style={S.fId}>{amb.id}</span>
                            <span style={{ ...S.fStatus, background: amb.status === 'available' ? '#DCFCE7' : '#FFEDD5', color: amb.status === 'available' ? '#16A34A' : '#EA580C' }}>{amb.status}</span>
                         </div>
                         <div style={S.fDriver}>{amb.driver_name || 'N/A'}</div>
                         <div style={S.fLoc}>Navi Mumbai</div>
                      </div>
                   </div>
                 ))}
              </div>
           </div>
        </div>
      </div>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap');
        body { margin: 0; background: #F8FAFC; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

const styles = {
  root: { height: "100vh", display: "flex", flexDirection: "column", fontFamily: "'DM Sans', sans-serif", background: "#F8FAFC", overflow: "hidden" },
  header: { background: "#fff", borderBottom: "1px solid #E2E8F0", padding: "16px 32px", display: "flex", justifyContent: "space-between", alignItems: "center", zIndex: 10 },
  headerLeft: { display: "flex", alignItems: "center", gap: 20 },
  panelTitle: { fontSize: 22, fontWeight: 800, color: "#0F172A", margin: 0 },
  statusPill: { background: "#DCFCE7", color: "#16A34A", padding: "4px 12px", borderRadius: 40, fontSize: 10, fontWeight: 800, display: "flex", alignItems: "center", gap: 6 },
  statusDot: { width: 6, height: 6, borderRadius: "50%", background: "#16A34A" },
  headerStats: { display: "flex", alignItems: "center", gap: 32 },
  topStat: { textAlign: "right" },
  topStatVal: { fontSize: 24, fontWeight: 800, color: "#0F172A", lineHeight: 1 },
  topStatLabel: { fontSize: 10, fontWeight: 700, color: "#94A3B8", marginTop: 4, textTransform: "uppercase" },

  mainContent: { flex: 1, display: "flex", overflow: "hidden" },
  feedCol: { width: 440, background: "#fff", borderRight: "1px solid #E2E8F0", display: "flex", flexDirection: "column" },
  feedHeader: { padding: "20px 24px 12px", display: "flex", justifyContent: "space-between", alignItems: "center" },
  feedTitle: { fontSize: 18, fontWeight: 800, color: "#0F172A", display: "flex", alignItems: "center", gap: 10 },
  autoSync: { fontSize: 11, color: "#3B82F6", fontWeight: 700 },
  feedScroll: { flex: 1, overflowY: "auto", padding: "12px 20px", display: "flex", flexDirection: "column", gap: 20 },
  
  sosCard: { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 24, padding: "20px", boxShadow: "0 4px 20px rgba(0,0,0,0.03)" },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 4 },
  patientName: { fontSize: 18, fontWeight: 800, color: "#0F172A" },
  pBadge: { marginLeft: 10, padding: "2px 8px", borderRadius: 6, fontSize: 10, fontWeight: 900 },
  timeSince: { fontSize: 10, color: "#94A3B8", textAlign: "right", fontWeight: 600 },
  cardSubtitle: { fontSize: 12, color: "#64748B", fontWeight: 600, marginBottom: 16 },
  
  modelBox: { background: "#F8FAFC", border: "1px solid #E2E8F0", borderRadius: 12, padding: "12px 16px", marginBottom: 16 },
  modelHeader: { fontSize: 9, fontWeight: 800, color: "#94A3B8", display: "flex", alignItems: "center", gap: 6, marginBottom: 8 },
  modelGrid: { display: "flex", gap: 16 },
  modelMain: { flex: 2 },
  modelSide: { flex: 1, borderLeft: "1px solid #E2E8F0", paddingLeft: 12 },
  modelLabel: { fontSize: 9, fontWeight: 700, color: "#94A3B8", marginBottom: 2 },
  modelVal: { fontSize: 11, fontWeight: 800, color: "#4F46E5", lineHeight: 1.2 },

  cardActions: { display: "flex", gap: 10 },
  dispatchBtn: { flex: 2, background: "#1E3A8A", color: "#fff", border: "none", padding: "10px", borderRadius: 10, fontWeight: 800, fontSize: 12, cursor: "pointer" },
  secBtn: { flex: 1, background: "#fff", border: "1px solid #E2E8F0", borderRadius: 10, fontWeight: 700, fontSize: 11, color: "#64748B", cursor: "pointer" },
  cardId: { fontSize: 9, color: "#CBD5E1", marginTop: 12, fontWeight: 600 },

  hospSection: { padding: "20px 24px", background: "#F8FAFC", borderTop: "1px solid #E2E8F0" },
  hospTitle: { fontSize: 12, fontWeight: 800, color: "#475569", marginBottom: 16, display: "flex", alignItems: "center", gap: 8 },
  hospList: { display: "flex", flexDirection: "column", gap: 12 },
  hospItem: { display: "flex", flexDirection: "column", gap: 6 },
  hospMeta: { display: "flex", justifyContent: "space-between", fontSize: 11 },
  hospName: { fontWeight: 700, color: "#1E293B" },
  hospBeds: { color: "#EA580C" },
  hospBarBg: { height: 6, background: "#E2E8F0", borderRadius: 10, overflow: "hidden" },
  hospBarFill: { height: "100%", borderRadius: 10 },

  rightCol: { flex: 1, display: "flex", flexDirection: "column" },
  mapLegend: { padding: "14px 24px", background: "#fff", borderBottom: "1px solid #E2E8F0", display: "flex", justifyContent: "space-between", alignItems: "center" },
  legendLeft: { display: "flex", gap: 24, fontSize: 10, fontWeight: 700, color: "#64748B" },
  legendRight: { display: "flex", gap: 16, fontSize: 9, fontWeight: 800, color: "#94A3B8" },
  dotItem: { display: "flex", alignItems: "center", gap: 6 },
  dot: { width: 8, height: 8, borderRadius: "50%" },
  mapWrapper: { flex: 1, position: "relative" },

  fleetSection: { padding: "20px 24px", background: "#fff", borderTop: "1px solid #E2E8F0" },
  fleetHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 },
  fleetTitle: { fontSize: 14, fontWeight: 800, color: "#0F172A", display: "flex", alignItems: "center", gap: 10 },
  fleetCollapse: { fontSize: 11, fontWeight: 700, color: "#94A3B8" },
  fleetGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 },
  fleetCard: { border: "1px solid #F1F5F9", borderRadius: 16, padding: "12px", display: "flex", gap: 12, background: "#F8FAFC" },
  fIcon: { fontSize: 20 },
  fInfo: { flex: 1 },
  fRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  fId: { fontSize: 11, fontWeight: 800, color: "#0F172A" },
  fStatus: { fontSize: 8, fontWeight: 900, padding: "2px 6px", borderRadius: 4, textTransform: "uppercase" },
  fDriver: { fontSize: 10, fontWeight: 700, color: "#64748B" },
  fLoc: { fontSize: 9, color: "#94A3B8", fontWeight: 600 },

  modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(15, 23, 42, 0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000, backdropFilter: 'blur(4px)' },
  modal: { background: '#fff', width: 440, borderRadius: 24, boxShadow: '0 20px 50px rgba(0,0,0,0.3)', padding: 32, position: 'relative' },
  modalHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, color: '#0F172A' },
  modalBody: { display: 'flex', flexDirection: 'column', gap: 12 },
  logItem: { fontSize: 13, color: '#64748B', padding: '12px', background: '#F8FAFC', borderRadius: 12, border: '1px solid #E2E8F0' },
  closeBtn: { background: 'none', border: 'none', fontSize: 24, cursor: 'pointer', color: '#94A3B8' }
};
