"use client";
import { Shield, Activity, Map, Settings, User, LogOut, Phone, Home } from "lucide-react";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const S = styles;
  const [citizenName, setCitizenName] = useState("No Active Signal");
  const [citizenPhone, setCitizenPhone] = useState("");
  const [hospitals, setHospitals] = useState([]);
  const pathname = usePathname();

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    const checkSync = async () => {
      try {
        const res = await fetch(`${backendUrl}/incidents/active`);
        const iData = await res.json();
        
        if (iData.incidents?.length > 0) {
          setCitizenName(iData.incidents[0].patient_name || "Active Signal");
          setCitizenPhone(iData.incidents[0].phone || "");
        } else {
          setCitizenName("No Active SOS Signal");
          setCitizenPhone("");
        }
      } catch (e) {
        console.error("Sidebar Sync Error:", e);
        setCitizenName("Sync Offline");
      }

      // Hospital Sync from DB with proximity sorting
      try {
        const hRes = await fetch(`${backendUrl}/hospitals`);
        const hData = await hRes.json();
        let rawHospitals = hData.hospitals || [];

        // If there's an active citizen, sort hospitals by distance
        if (iData.incidents?.length > 0) {
          const cLat = iData.incidents[0].latitude;
          const cLng = iData.incidents[0].longitude;

          rawHospitals = rawHospitals.map(h => {
            // Simple distance approximation
            const dist = Math.sqrt(
              Math.pow(h.latitude - cLat, 2) + Math.pow(h.longitude - cLng, 2)
            ) * 111; // 1 degree ~ 111km
            return { ...h, distance: dist };
          }).sort((a, b) => a.distance - b.distance);
        }

        setHospitals(rawHospitals.slice(0, 5)); // Show top 5 nearest
      } catch (e) {
        console.error("Hospital Fetch Error:", e);
      }
    };

    checkSync();
    window.addEventListener('storage', checkSync);
    const interval = setInterval(checkSync, 5000);
    return () => {
      window.removeEventListener('storage', checkSync);
      clearInterval(interval);
    };
  }, [backendUrl]);

  const handleContact = () => {
    if (citizenPhone) {
      window.location.href = `tel:${citizenPhone}`;
    } else {
      alert("No phone number available for this citizen.");
    }
  };

  const handleAction = (type) => {
    alert(`${type} module is being initialized for production.`);
  };

  const isActive = (path) => pathname === path;

  return (
    <div style={styles.sidebar}>
      {/* BRAND SECTION */}
      <div style={S.brand}>
         <div style={S.logoContainer}>
            <div style={S.logoGlow} />
            <div style={S.logoBox}>
               <Shield size={22} color="#fff" style={{ position: 'absolute' }} />
               <Activity size={12} color="#06B6D4" strokeWidth={3} style={{ position: 'relative', top: 2 }} />
            </div>
         </div>
         <div>
            <h1 style={S.brandName}>NaviRaksha</h1>
            <p style={S.brandSubText}>INTELLIGENCE GRID</p>
         </div>
      </div>

      {/* NAVIGATION */}
      <div style={styles.nav}>
        <Link href="/dispatcher" style={{ ...styles.navBtn, ...(isActive('/dispatcher') ? styles.navActive : {}) }}>
          <Activity size={18} /> Command Center
        </Link>
        <Link href="/simulation" style={{ ...styles.navBtn, ...(isActive('/simulation') ? styles.navActive : {}) }}>
          <Map size={18} /> Simulation Engine
        </Link>
      </div>

      {/* OPERATIONAL WIDGETS (HIDE IN SIMULATION) */}
      {pathname !== '/simulation' && (
        <>
          {/* HOSPITAL WIDGET */}
          <div style={S.widget}>
            <div style={S.widgetHeader}>
               <Home size={14} /> Hospital Capacity
            </div>
            {hospitals.length > 0 ? hospitals.map(h => {
              const total = h.total_beds || 100;
              const avail = h.available_beds || 0;
              const pct = Math.min(100, (avail / total) * 100);
              return (
                <div key={h.id} style={{ marginBottom: 12 }}>
                   <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, fontWeight: 700, marginBottom: 4 }}>
                      <span style={{ maxWidth: '70%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {h.name} {h.distance && <span style={{ color: '#6366F1', fontWeight: 500 }}>• {h.distance.toFixed(1)}km</span>}
                      </span>
                      <span style={{ color: '#EA580C' }}>{avail} beds</span>
                   </div>
                   <div style={{ height: 6, background: '#E2E8F0', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{ width: `${pct}%`, height: '100%', background: '#16A34A', borderRadius: 3 }} />
                   </div>
                </div>
              );
            }) : (
              <div style={{ fontSize: 11, color: '#94A3B8', textAlign: 'center', padding: '10px 0' }}>No hospital data connected</div>
            )}
          </div>

          {/* CITIZEN INTERACTION */}
          <div style={styles.citizenProfile}>
             <div style={styles.profileHeader}>ACTIVE CITIZEN</div>
             <div style={styles.profileCard}>
                <div style={styles.avatar}>{citizenName === "No Active Signal" ? "N" : citizenName.charAt(0).toUpperCase()}</div>
                <div style={styles.profileInfo}>
                   <div style={styles.profileName}>{citizenName}</div>
                   <div style={styles.profileStatus}>
                      {citizenPhone ? (
                        <><Phone size={10} color="#10B981" /> {citizenPhone}</>
                      ) : (
                        <><span style={styles.onlineDot} /> Session Active</>
                      )}
                   </div>
                </div>
             </div>
             <div style={styles.profileAction} onClick={handleContact}>
                <Phone size={12} /> Contact Citizen
             </div>
          </div>
        </>
      )}

      {/* FOOTER ACTIONS */}
      <div style={styles.footer}>
        <button style={styles.footerBtn} onClick={() => handleAction('Settings')}><Settings size={16} /> Settings</button>
        <button style={styles.footerBtn} onClick={() => handleAction('Logout')}><LogOut size={16} /> Logout</button>
      </div>
    </div>
  );
}

const styles = {
  sidebar: { 
    width: 260, 
    background: "#fff", 
    borderRight: "1px solid #E2E8F0", 
    display: "flex", 
    flexDirection: "column", 
    padding: "24px 16px", 
    height: "100vh", 
    position: "relative",
    fontFamily: "'Inter', sans-serif"
  },
  brand: { display: "flex", alignItems: "center", gap: 16, marginBottom: 48, padding: "0 8px" },
  logoContainer: { position: 'relative', width: 48, height: 48 },
  logoGlow: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'linear-gradient(135deg, #4F46E5, #06B6D4)', borderRadius: 14, filter: 'blur(8px)', opacity: 0.4 },
  logoBox: { position: 'relative', width: 48, height: 48, background: 'linear-gradient(135deg, #4F46E5, #06B6D4)', borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: '0 8px 16px rgba(79, 70, 229, 0.2)' },
  brandName: { fontSize: 18, fontWeight: 800, color: "#1E293B", margin: 0, letterSpacing: "-0.5px" },
  brandSubText: { fontSize: 9, fontWeight: 800, color: "#94A3B8", margin: 0, letterSpacing: "1px", textTransform: 'uppercase' },
  
  nav: { display: "flex", flexDirection: "column", gap: 8, flex: 1 },
  navBtn: { 
    display: "flex", 
    alignItems: "center", 
    gap: 12, 
    padding: "12px 16px", 
    borderRadius: 12, 
    textDecoration: "none",
    color: "#64748B", 
    fontSize: 14, 
    fontWeight: 600, 
    transition: "0.2s" 
  },
  navActive: { 
    background: "#6366F1", 
    color: "#fff", 
    boxShadow: "0 4px 14px rgba(99, 102, 241, 0.4)" 
  },
  
  widget: { 
    marginBottom: 32, 
    padding: "0 8px" 
  },
  widgetHeader: { 
    fontSize: 12, 
    fontWeight: 700, 
    color: "#1E293B", 
    marginBottom: 16, 
    display: "flex", 
    alignItems: "center", 
    gap: 8 
  },

  citizenProfile: { 
    background: "#F8FAFC", 
    borderRadius: 20, 
    padding: "20px 16px", 
    border: "1px solid #E2E8F0", 
    marginTop: "auto", 
    marginBottom: 24,
    boxShadow: "0 2px 8px rgba(0,0,0,0.02)"
  },
  profileHeader: { fontSize: 9, fontWeight: 800, color: "#94A3B8", letterSpacing: 1, marginBottom: 14 },
  profileCard: { display: "flex", alignItems: "center", gap: 12 },
  avatar: { 
    width: 40, 
    height: 40, 
    borderRadius: 12, 
    background: "#6366F1", 
    color: "#fff", 
    display: "flex", 
    alignItems: "center", 
    justifyContent: "center", 
    fontWeight: 800, 
    fontSize: 18 
  },
  profileInfo: { flex: 1 },
  profileName: { fontSize: 14, fontWeight: 700, color: "#1E293B", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 140 },
  profileStatus: { fontSize: 10, color: "#64748B", display: "flex", alignItems: "center", gap: 4, marginTop: 2 },
  onlineDot: { width: 6, height: 6, borderRadius: "50%", background: "#10B981" },
  profileAction: { 
    marginTop: 16, 
    fontSize: 10, 
    fontWeight: 700, 
    color: "#6366F1", 
    display: "flex", 
    alignItems: "center", 
    gap: 6, 
    cursor: "pointer",
    padding: "8px 12px",
    background: "#fff",
    borderRadius: 10,
    border: "1px solid #E2E8F0",
    textAlign: "center",
    justifyContent: "center"
  },
  
  footer: { borderTop: "1px solid #F1F5F9", paddingTop: 20, display: "flex", flexDirection: "column", gap: 4 },
  footerBtn: { 
    display: "flex", 
    alignItems: "center", 
    gap: 10, 
    padding: "10px 16px", 
    border: "none", 
    background: "none", 
    color: "#94A3B8", 
    fontSize: 13, 
    fontWeight: 600, 
    cursor: "pointer",
    width: "100%",
    textAlign: "left"
  }
};
