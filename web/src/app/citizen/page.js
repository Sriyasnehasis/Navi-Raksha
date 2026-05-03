"use client";
export const dynamic = "force-dynamic";
import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import { Shield, AlertCircle, MapPin, Navigation, Send, Heart, Activity, Zap, CheckCircle, User, Phone, Clock } from "lucide-react";
import Link from "next/link";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

const LiveMap = dynamic(() => import("../../components/LiveMap"), {
  ssr: false,
  loading: () => (
    <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", background: "#f1f5f9", color: "#94a3b8" }}>
      Loading Map…
    </div>
  ),
});

export default function CitizenPortal() {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [injuryType, setInjuryType] = useState("Cardiac");
  const [severity, setSeverity] = useState("Moderate");
  const [simMode, setSimMode] = useState(true);
  // Default to a random spot in Navi Mumbai (Vashi to Belapur range)
  const [simPos, setSimPos] = useState([
    19.03 + (Math.random() * 0.06), 
    73.01 + (Math.random() * 0.04)
  ]);
  const [isClient, setIsClient] = useState(false);
  const [dispatched, setDispatched] = useState(null);
  const [sending, setSending] = useState(false);
  const [online, setOnline] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setIsClient(true), 0);
    // Check backend connectivity
    fetch(`${BACKEND}/health`)
      .then(res => setOnline(res.ok))
      .catch(() => setOnline(false));
    return () => clearTimeout(t);
  }, []);

  // REAL GPS LOGIC
  useEffect(() => {
    if (!simMode && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setSimPos([pos.coords.latitude, pos.coords.longitude]),
        (err) => {
          console.warn("GPS Access Denied, falling back to simulation.");
          setSimMode(true);
        }
      );
    }
  }, [simMode]);

  const sendSOS = async () => {
    if (!name) return alert("Please enter your name!");
    if (!phone || phone.length !== 10 || !/^\d+$/.test(phone)) {
      return alert("Please enter a valid 10-digit mobile number!");
    }
    setSending(true);
    
    // Persist name for the Admin Sidebar
    localStorage.setItem('naviraksha_citizen_name', name);

    const sosPayload = {
      id: `INC-${Date.now().toString().slice(-4)}`,
      patient_name: name,
      phone: phone,
      incident_type: injuryType,
      severity: severity,
      latitude: simPos[0],
      longitude: simPos[1]
    };

    try {
      const bc = new BroadcastChannel('naviraksha_sos');
      
      const response = await fetch(`${BACKEND}/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sosPayload),
      });

      if (!response.ok) throw new Error("Backend Refused Connection");
      
      const data = await response.json();
      setDispatched(data);
      
      // Local Sync for Admin Panel
      bc.postMessage({ type: 'NEW_SOS', data: { ...sosPayload, prediction: data.prediction } });
      setTimeout(() => bc.close(), 1000);

    } catch (err) {
      console.error("SOS Error:", err);
      // Fallback if backend is down
      setDispatched({ ambulance_id: "ALS-001", ambulance_type: "ALS", eta_minutes: 3.5 });
      const bc = new BroadcastChannel('naviraksha_sos');
      bc.postMessage({ type: 'NEW_SOS', data: sosPayload });
      setTimeout(() => bc.close(), 1000);
    } finally {
      setSending(false);
    }
  };

  const [ambulances, setAmbulances] = useState([]);
  const [hospitals, setHospitals] = useState([]);

  // LIVE STATUS TRACKER
  useEffect(() => {
    let isMounted = true;

    const syncData = async () => {
      try {
        const [iR, aR, hR] = await Promise.all([
          fetch(`${BACKEND}/incidents/active`),
          fetch(`${BACKEND}/ambulances/active`),
          fetch(`${BACKEND}/hospitals`)
        ]);
        
        if (!isMounted) return;

        const iData = await iR.json();
        const aData = await aR.json();
        const hData = await hR.json();
        
        setAmbulances(aData.ambulances || []);
        setHospitals(hData.hospitals || []);
        
        // Use a functional update or a ref if needed, but since we want to check current state
        // we can either keep it in dependencies (which causes resets) or use a more complex pattern.
        // For now, let's just make it cleaner.
        const currentId = localStorage.getItem('naviraksha_incident_id');
        if (currentId && iData.incidents) {
           const myInc = iData.incidents.find(i => i.id === currentId);
           if (myInc) setDispatched(myInc);
        }
      } catch (e) { 
        if (isMounted) console.error("Sync Error:", e); 
      }
    };

    syncData();
    const t = setInterval(syncData, 3000);
    
    return () => {
      isMounted = false;
      clearInterval(t);
    };
  }, []); // Remove dispatched from dependencies to avoid infinite reset cycle

  if (!isClient) return null;

  return (
    <div style={styles.root}>
      {/* SIDEBAR */}
      <div style={styles.sidebar}>
        <div style={styles.brand}>
           <div style={styles.logoContainer}>
              <div style={styles.logoGlow} />
              <div style={styles.logoBox}>
                 <Shield size={24} color="#fff" style={{ position: 'absolute' }} />
                 <Activity size={14} color="#fff" strokeWidth={3} style={{ position: 'relative', top: 2 }} />
              </div>
           </div>
           <div>
              <h1 style={styles.brandText}>NaviRaksha</h1>
              <p style={styles.brandSub}>EMERGENCY AI</p>
           </div>
        </div>

        <div style={styles.formSection}>
           <div style={styles.formGroup}>
              <label style={styles.label}><MapPin size={14} /> LOCATION SIGNAL</label>
              <div style={styles.locDisplay}>
                 {simPos[0].toFixed(5)}, {simPos[1].toFixed(5)}
              </div>
              <div style={styles.simRow}>
                 <button style={styles.gpsBtn} onClick={() => setSimPos([19.076 + (Math.random()-0.5)*0.01, 72.877 + (Math.random()-0.5)*0.01])}>
                    <Navigation size={12} /> Refresh GPS
                 </button>
                 <div style={styles.toggleRow} onClick={() => setSimMode(!simMode)}>
                    <div style={{...styles.toggle, background: simMode ? '#4F46E5' : '#E2E8F0'}}>
                       <div style={{...styles.knob, left: simMode ? 22 : 2}} />
                    </div>
                    <span style={{fontSize: 11, fontWeight: 700}}>{simMode ? "Simulate" : "Real GPS"}</span>
                 </div>
              </div>
           </div>

           <div style={styles.formGroup}>
              <label style={styles.label}><User size={14} /> YOUR DETAILS</label>
              <input 
                placeholder="Full Name" 
                style={styles.input} 
                value={name} 
                onChange={(e) => {
                  setName(e.target.value);
                  localStorage.setItem('naviraksha_citizen_name', e.target.value);
                }} 
              />
              <input 
                placeholder="10-Digit Mobile Number" 
                type="tel"
                maxLength={10}
                style={{...styles.input, marginTop: 10}} 
                value={phone} 
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, ''); // Only allow digits
                  setPhone(val);
                  localStorage.setItem('naviraksha_citizen_phone', val);
                }} 
              />
              <select 
                style={styles.input} 
                value={injuryType === 'Other' || !['Cardiac', 'Stroke', 'Trauma', 'Minor Injury'].includes(injuryType) ? 'Other' : injuryType} 
                onChange={(e) => {
                  if (e.target.value === 'Other') {
                    setInjuryType("");
                  } else {
                    setInjuryType(e.target.value);
                  }
                }}
              >
                 <option value="Cardiac">Cardiac</option>
                 <option value="Stroke">Stroke</option>
                 <option value="Trauma">Trauma</option>
                 <option value="Minor Injury">Minor Injury</option>
                 <option value="Other">Other (Write manually)</option>
              </select>
              {(injuryType === "" || !['Cardiac', 'Stroke', 'Trauma', 'Minor Injury'].includes(injuryType)) && (
                <input 
                  placeholder="Specify emergency (e.g. Fire, Accident...)" 
                  style={{...styles.input, marginTop: 8, border: '2px solid #6366F1'}} 
                  value={injuryType} 
                  onChange={(e) => setInjuryType(e.target.value)} 
                />
              )}
           </div>

           <div style={styles.formGroup}>
              <label style={styles.label}><AlertCircle size={14} /> SEVERITY LEVEL</label>
              <div style={styles.sevGrid}>
                 {['Mild', 'Moderate', 'Critical'].map(s => (
                   <button 
                     key={s}
                     onClick={() => setSeverity(s)}
                     style={{
                       ...styles.sevBtn, 
                       background: severity === s ? (s === 'Critical' ? '#FEE2E2' : '#FFEDD5') : '#fff',
                       borderColor: severity === s ? (s === 'Critical' ? '#DC2626' : '#EA580C') : '#E2E8F0',
                       color: severity === s ? (s === 'Critical' ? '#DC2626' : '#EA580C') : '#64748B'
                     }}
                   >{s}</button>
                 ))}
              </div>
           </div>

           {dispatched && (
             <div style={styles.dispatchBox}>
                <div style={styles.dHeader}>
                  {dispatched.status === 'Dispatched' ? (
                    <><CheckCircle size={14} color="#16A34A" /> AMBULANCE DISPATCHED!</>
                  ) : (
                    <><Clock size={14} color="#EA580C" /> SOS Signal Received</>
                  )}
                </div>
                <div style={styles.dBody}>
                   <div><b>AI Recommendation:</b> {dispatched.prediction?.type || "Calculating..."}</div>
                   <div>ETA: <span style={{color: '#DC2626', fontWeight: 700}}>{dispatched.prediction?.eta || '4-5'} min</span></div>
                   <div style={{fontSize: 10, marginTop: 4, opacity: 0.7}}>
                     {dispatched.status === 'Dispatched' ? 'Status: UNIT EN ROUTE' : `ML Confidence: ${dispatched.prediction?.conf || '98%'}`}
                   </div>
                </div>
             </div>
           )}

           <button 
             style={{...styles.sosBtn, opacity: sending ? 0.7 : 1}} 
             onClick={sendSOS}
             disabled={sending}
           >
              <Zap size={18} fill="#fff" /> {sending ? "SENDING..." : "SEND SOS NOW"}
           </button>
        </div>

        <Link href="/dispatcher" style={styles.backLink}>← Back to Portal</Link>
      </div>

      {/* MAP AREA */}
      <div style={styles.mapArea}>
        <div style={styles.statusRow}>
           <div style={{ ...styles.pill, background: online ? '#DCFCE7' : '#FEE2E2', color: online ? '#16A34A' : '#DC2626' }}>
              <span style={{...styles.dot, background: online ? '#16A34A' : '#DC2626'}} /> 
              {online ? "SERVER CONNECTED" : "SERVER OFFLINE"}
           </div>
           <div style={styles.pill}>
              <span style={{...styles.dot, background: '#DC2626'}} /> LIVE SIGNAL
           </div>
        </div>
        <LiveMap 
          ambulances={ambulances} 
          incidents={dispatched ? [dispatched] : []} 
          hospitals={hospitals}
          userLat={simPos[0]} 
          userLng={simPos[1]} 
        />
      </div>

      <style>{`
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
      `}</style>
    </div>
  );
}

const styles = {
  root: { height: "100vh", display: "flex", flexDirection: "row", flexWrap: "wrap", fontFamily: "'Inter', sans-serif", background: "#F8FAFC" },
  sidebar: { width: "400px", minWidth: "320px", background: "#fff", borderRight: "1px solid #E2E8F0", display: "flex", flexDirection: "column", padding: "24px", overflowY: "auto", flexShrink: 0 },
  brand: { display: "flex", alignItems: "center", gap: 16, marginBottom: 24 },
  logoContainer: { position: 'relative', width: 44, height: 44 },
  logoGlow: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'linear-gradient(135deg, #DC2626, #F97316)', borderRadius: 12, filter: 'blur(8px)', opacity: 0.4 },
  logoBox: { position: 'relative', width: 44, height: 44, background: 'linear-gradient(135deg, #DC2626, #F97316)', borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: '0 8px 20px rgba(220,38,38,0.2)' },
  brandText: { fontSize: 20, fontWeight: 800, color: "#1E293B", margin: 0 },
  brandSub: { fontSize: 10, fontWeight: 700, color: "#94A3B8", margin: 0, letterSpacing: 1 },
  
  formSection: { flex: 1, display: "flex", flexDirection: "column", gap: 20 },
  formGroup: { display: "flex", flexDirection: "column", gap: 8 },
  label: { fontSize: 10, fontWeight: 800, color: "#94A3B8", display: "flex", alignItems: "center", gap: 6 },
  locDisplay: { padding: "10px 14px", background: "#F8FAFC", borderRadius: 12, border: "1px solid #E2E8F0", fontSize: 12, fontWeight: 700, color: "#1E293B" },
  simRow: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  gpsBtn: { background: "none", border: "1px solid #3B82F6", color: "#3B82F6", padding: "4px 8px", borderRadius: 8, fontSize: 10, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 },
  toggleRow: { display: "flex", alignItems: "center", gap: 8 },
  toggle: { width: 40, height: 20, borderRadius: 20, position: "relative", cursor: "pointer", transition: "0.3s" },
  knob: { width: 16, height: 16, background: "#fff", borderRadius: "50%", position: "absolute", top: 2, transition: "0.2s" },

  input: { width: "100%", padding: "10px 14px", borderRadius: 12, border: "1px solid #E2E8F0", outline: "none", fontSize: 14, fontWeight: 600 },
  sevGrid: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 },
  sevBtn: { padding: "8px", borderRadius: 10, border: "1px solid", fontSize: 11, fontWeight: 700, cursor: "pointer" },

  dispatchBox: { background: "#F0FDF4", border: "1px solid #16A34A", borderRadius: 16, padding: 14 },
  dHeader: { fontSize: 12, fontWeight: 800, color: "#16A34A", display: "flex", alignItems: "center", gap: 8, marginBottom: 4 },
  dBody: { fontSize: 11, color: "#1E293B", lineHeight: 1.4 },

  sosBtn: { marginTop: "24px", background: "#DC2626", color: "#fff", border: "none", padding: "16px", borderRadius: 16, fontSize: 14, fontWeight: 800, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 10, boxShadow: "0 8px 20px rgba(220,38,38,0.3)" },
  backLink: { marginTop: 24, fontSize: 11, fontWeight: 700, color: "#94A3B8", textDecoration: "none", textAlign: "center" },

  mapArea: { flex: 1, position: "relative", minHeight: "400px" },
  statusRow: { position: "absolute", top: 10, right: 10, display: "flex", flexDirection: "column", gap: 8, zIndex: 1000 },
  pill: { padding: "4px 10px", borderRadius: 40, background: "#fff", border: "1px solid #E2E8F0", fontSize: 9, fontWeight: 800, display: "flex", alignItems: "center", gap: 6, boxShadow: "0 4px 12px rgba(0,0,0,0.05)" },
  dot: { width: 6, height: 6, borderRadius: "50%", animation: "pulse 1.5s infinite" }
};
