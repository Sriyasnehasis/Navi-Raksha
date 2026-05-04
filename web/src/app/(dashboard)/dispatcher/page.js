"use client";
export const dynamic = "force-dynamic";
import { useState, useEffect } from "react";
import nextDynamic from "next/dynamic";
import { Activity, Zap, Phone, Shield, Clock } from "lucide-react";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "https://navi-raksha-backend.onrender.com";

const LiveMap = nextDynamic(() => import("../../../components/LiveMap"), {
  ssr: false,
  loading: () => <div style={{width:"100%",height:"100%",background:"#f1f5f9",display:"flex",alignItems:"center",justifyContent:"center"}}>Loading Intelligence Map...</div>,
});

const INC_BORDER = { cardiac: "#DC2626", trauma: "#EA580C", respiratory: "#CA8A04", burn: "#9333EA", default: "#6B7280" };

export default function AdminPanel() {
  const [ambulances, setAmbulances] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [selectedAmb, setSelectedAmb] = useState({});
  const [showLogs, setShowLogs] = useState(null);

  const fetchData = async () => {
    try {
      const [aR, iR, hR] = await Promise.all([
        fetch(`${BACKEND}/ambulances/active`),
        fetch(`${BACKEND}/incidents/active`),
        fetch(`${BACKEND}/hospitals`),
      ]);
      setAmbulances((await aR.json()).ambulances || []);
      setIncidents((await iR.json()).incidents || []);
      setHospitals((await hR.json()).hospitals || []);
    } catch (e) { console.error("Sync Error:", e); }
  };

  useEffect(() => {
    fetchData();
    const t = setInterval(fetchData, 4000);
    return () => clearInterval(t);
  }, []);

  const handleVerify = async (incId) => {
    const ambId = selectedAmb[incId];
    if (!ambId) return alert("CRITICAL: Please select an ambulance unit first!");
    try {
      const res = await fetch(`${BACKEND}/dispatch/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incident_id: incId, ambulance_id: ambId })
      });
      if (res.ok) fetchData();
      else alert("Dispatch failed.");
    } catch (err) { alert("Error: " + err.message); }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", fontFamily: "'DM Sans', sans-serif", background: "#F8FAFC" }}>
      <div style={{ background: "#fff", borderBottom: "1px solid #E2E8F0", padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", zIndex: 10 }}>
        <h2 style={{ fontSize: 18, fontWeight: 800, color: "#0F172A", margin: 0 }}>Admin Intelligence Panel</h2>
        <div style={{ display: "flex", gap: 20 }}>
          <div style={{textAlign:"right"}}><div style={{fontSize:18,fontWeight:800}}>{incidents.length}</div><div style={{fontSize:9,color:"#94A3B8"}}>ACTIVE SOS</div></div>
          <div style={{textAlign:"right"}}><div style={{fontSize:18,fontWeight:800}}>{ambulances.filter(a=>a.status==='available').length}</div><div style={{fontSize:9,color:"#94A3B8"}}>AVAIL UNITS</div></div>
          <button onClick={() => fetch(`${BACKEND}/admin/cleanup`, {method:'POST'}).then(fetchData)} style={{ background: '#FEF2F2', border: '1px solid #FEE2E2', borderRadius: '6px', padding: '6px 12px', fontSize: '11px', color: '#DC2626', cursor: 'pointer', fontWeight: 800 }}>RESET GRID</button>
        </div>
      </div>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <div style={{ width: "420px", background: "#fff", borderRight: "1px solid #E2E8F0", display: "flex", flexDirection: "column" }}>
          <div style={{ padding: "16px", borderBottom: "1px solid #F1F5F9", fontSize: 16, fontWeight: 800, display: "flex", alignItems: "center", gap: 8 }}>
            <Zap size={18} fill="#EA580C" color="#EA580C" /> SOS Intelligence Feed
          </div>
          <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
            {incidents.map(inc => (
              <div key={inc.id} style={{ border: "1px solid #E2E8F0", borderRadius: 16, padding: "16px", marginBottom: 16, borderLeft: `6px solid ${INC_BORDER[inc.incident_type?.toLowerCase()] || '#64748b'}`, background: inc.status==='Dispatched'?'#F0FDF4':'#fff' }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontWeight: 800, fontSize: 15 }}>{inc.patient_name} <span style={{fontSize:9, background:"#f1f5f9", padding:"2px 6px", borderRadius:4, marginLeft:6}}>{inc.severity}</span></span>
                  <span style={{ fontSize: 10, fontWeight: 900, color: inc.status==='Dispatched'?'#16A34A':'#64748B' }}>{inc.status.toUpperCase()}</span>
                </div>
                <div style={{ fontSize: 11, color: "#64748B", marginBottom: 12 }}>{inc.incident_type} · {inc.location_address}</div>
                
                <div style={{ background: "#F8FAFC", border:"1px solid #E2E8F0", borderRadius: 12, padding: "10px", marginBottom: 12 }}>
                  <div style={{ fontSize: 8, fontWeight: 800, color: "#94A3B8", marginBottom: 6, display:"flex", alignItems:"center", gap:4 }}><Shield size={10} /> RF MODEL RECOMMENDATION</div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <div><div style={{fontSize:8,color:"#94A3B8"}}>Rec. Unit</div><div style={{fontSize:11,fontWeight:800,color:"#4F46E5"}}>{inc.prediction?.type || "ALS"}</div></div>
                    <div><div style={{fontSize:8,color:"#94A3B8"}}>Est. ETA</div><div style={{fontSize:11,fontWeight:800,color:"#4F46E5"}}>{inc.prediction?.eta || "4.2 min"}</div></div>
                  </div>

                  {inc.prediction?.features_used && (
                    <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid #E2E8F0', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '4px 8px' }}>
                       <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>TRAFFIC: <span style={{ color: '#475569' }}>{inc.prediction.features_used.hour >= 8 && inc.prediction.features_used.hour <= 10 ? 'HIGH' : 'STABLE'}</span></div>
                       <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>WEATHER: <span style={{ color: '#475569' }}>{inc.prediction.features_used.is_raining ? '🌧️ RAIN' : '☀️ CLEAR'}</span></div>
                       <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>DRIVER: <span style={{ color: '#475569' }}>LVL {inc.prediction.features_used.driver_exp}</span></div>
                       <div style={{ fontSize: 7, color: '#94A3B8', fontWeight: 700 }}>ZONE VIOL: <span style={{ color: '#475569' }}>{inc.prediction.features_used.violations_zone}</span></div>
                    </div>
                  )}
                </div>

                {inc.status === 'Waiting' && (
                  <div style={{ marginBottom: 12 }}>
                    <div style={{fontSize:8,fontWeight:800,color:"#64748B",marginBottom:4}}>ASSIGN AMBULANCE UNIT</div>
                    <select 
                      value={selectedAmb[inc.id] || ""} 
                      onChange={(e) => setSelectedAmb({...selectedAmb, [inc.id]: e.target.value})}
                      style={{ width: '100%', padding: '8px', borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '11px', fontWeight: 800 }}
                    >
                      <option value="">-- Choose Unit --</option>
                      {ambulances.filter(a => a.status === 'available').map(a => (
                        <option key={a.id} value={a.id}>{a.id} ({a.type}) - {a.driver_name}</option>
                      ))}
                    </select>
                  </div>
                )}

                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={() => handleVerify(inc.id)} disabled={inc.status !== 'Waiting'} style={{ flex: 2, background: inc.status === 'Dispatched' ? '#16A34A' : '#1E3A8A', color: "#fff", border: "none", padding: "10px", borderRadius: 8, fontWeight: 800, fontSize: 11, cursor: "pointer" }}>
                    {inc.status === 'Dispatched' ? 'Unit Dispatched' : 'Verify & Dispatch'}
                  </button>
                  <button onClick={() => setShowLogs(inc)} style={{ flex: 1, background: "#fff", border: "1px solid #E2E8F0", borderRadius: 8, fontSize: 10, fontWeight: 700, color: "#64748B", cursor: "pointer" }}>Logs</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <div style={{ flex: 1, position: "relative" }}>
            <LiveMap ambulances={ambulances} incidents={incidents} hospitals={hospitals} isCitizenView={false} />
          </div>
          <div style={{ padding: "16px", background: "#fff", borderTop: "1px solid #E2E8F0" }}>
             <div style={{fontSize:12,fontWeight:800,marginBottom:12,display:"flex",alignItems:"center",gap:8}}><Activity size={16} /> Active Fleet Real-time Telemetry</div>
             <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
                {ambulances.map(amb => (
                  <div key={amb.id} style={{ border: "1px solid #F1F5F9", borderRadius: 12, padding: "12px", background: "#F8FAFC" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom:4 }}>
                      <span style={{fontSize:11,fontWeight:800}}>{amb.id}</span>
                      <span style={{fontSize:8,fontWeight:900,background:amb.status==='available'?'#DCFCE7':'#FFEDD5',color:amb.status==='available'?'#16A34A':'#EA580C',padding:"2px 6px",borderRadius:6}}>{amb.status.toUpperCase()}</span>
                    </div>
                    <div style={{fontSize:10,fontWeight:700,color:"#64748B"}}>{amb.driver_name}</div>
                  </div>
                ))}
             </div>
          </div>
        </div>
      </div>

      {showLogs && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(15, 23, 42, 0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000, backdropFilter: 'blur(4px)' }} onClick={() => setShowLogs(null)}>
           <div style={{ background: '#fff', width: "90%", maxWidth: "440px", borderRadius: 20, padding: 24, position: 'relative' }} onClick={e => e.stopPropagation()}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                 <h3 style={{ margin: 0, fontSize: 18, fontWeight:800 }}>Intelligence Log: {showLogs.patient_name}</h3>
                 <button onClick={() => setShowLogs(null)} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer', color: '#94A3B8' }}>×</button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                 <div style={{ fontSize: 12, color: '#64748B', padding: '12px', background: '#F8FAFC', borderRadius: 10, border: '1px solid #E2E8F0' }}>
                    <div style={{ fontWeight: 800, color: '#1E3A8A', fontSize: 10, marginBottom:4 }}>SIGNAL RECEIVED</div>
                    SOS intelligence uplink established from {showLogs.location_address}.
                 </div>
                 {showLogs.prediction?.features_used && (
                   <div style={{ fontSize: 12, color: '#64748B', padding: '12px', background: '#F8FAFC', borderRadius: 10, border: '1px solid #E2E8F0', borderLeft: '4px solid #4F46E5' }}>
                      <div style={{ fontWeight: 800, color: '#4F46E5', fontSize: 10, marginBottom:6 }}>DEEP INTELLIGENCE AUDIT</div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                         <div>• Traffic: {showLogs.prediction.features_used.hour >= 8 && showLogs.prediction.features_used.hour <= 10 ? 'HEAVY' : 'NORMAL'}</div>
                         <div>• Weather: {showLogs.prediction.features_used.is_raining ? 'RAINING' : 'CLEAR'}</div>
                         <div>• Zone Violations: {showLogs.prediction.features_used.violations_zone}</div>
                         <div>• Driver Exp: Lvl {showLogs.prediction.features_used.driver_exp}</div>
                      </div>
                   </div>
                 )}
              </div>
           </div>
        </div>
      )}
    </div>
  );
}
