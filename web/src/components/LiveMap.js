"use client";
import React, { useEffect, useState, memo } from "react";
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// ── LEAFLET ICON FIX ─────────────────────────────────────────────────────────
// This must only run in the browser
if (typeof window !== "undefined") {
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  });
}

const TYPE_COLORS = { ALS: '#dc2626', BLS: '#ea580c', BIKE: '#16a34a', MINI: '#16a34a' };
const SEV_COLORS  = { critical: '#dc2626', moderate: '#f97316', mild: '#eab308', minor: '#16a34a' };
const SEV_RADIUS  = { critical: 15, moderate: 11, mild: 8, minor: 6 };

function MapUpdater({ center, incidents, isCitizenView }) {
  const map = useMap();
  
  useEffect(() => {
    if (isCitizenView && incidents.length > 0) {
      const victimPos = [incidents[0].latitude, incidents[0].longitude];
      map.setView(victimPos, 15);
    } else {
      map.setView(center);
    }
  }, [center, map, isCitizenView, incidents]);
  
  return null;
}

const LiveMap = memo(({ ambulances = [], incidents = [], hospitals = [], userLat, userLng, isCitizenView = false }) => {
  const [isMounted, setIsMounted] = useState(false);
  const center = [userLat || 19.076, userLng || 72.877];

  useEffect(() => {
    const t = setTimeout(() => setIsMounted(true), 0);
    return () => clearTimeout(t);
  }, []);

  if (!isMounted) return (
    <div style={{ width: "100%", height: "100%", background: "#f1f5f9", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "16px", color: "#94a3b8" }}>
      Initializing Map Grid...
    </div>
  );

  return (
    <div id="map-root-container" style={{ height: "100%", width: "100%", borderRadius: "24px", overflow: "hidden", border: "1px solid rgba(226, 232, 240, 0.8)", position: 'relative', boxShadow: '0 20px 50px rgba(0,0,0,0.1)' }}>
      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
          70% { transform: scale(1.15); box-shadow: 0 0 0 20px rgba(99, 102, 241, 0); }
          100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
        }
        .leaflet-control-zoom {
          border: none !important;
          margin: 20px !important;
          box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
          backdrop-filter: blur(8px);
        }
        .leaflet-control-zoom-in, .leaflet-control-zoom-out {
          background: rgba(255, 255, 255, 0.8) !important;
          color: #1E293B !important;
          border: 1px solid rgba(255,255,255,0.3) !important;
          font-weight: bold !important;
          width: 40px !important;
          height: 40px !important;
          line-height: 40px !important;
        }
        .leaflet-container {
          background: #f8fafc !important;
        }
      `}</style>
      <MapContainer 
        key="naviraksha-static-map"
        center={center} 
        zoom={13} 
        style={{ height: "100%", width: "100%", zIndex: 1 }}
        zoomControl={true}
        scrollWheelZoom={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <MapUpdater 
          center={center} 
          incidents={incidents} 
          isCitizenView={isCitizenView} 
        />

        {/* Dynamic Data Layers */}
        <CircleMarker center={center} radius={10} color="#3b82f6" fillColor="#3b82f6" fillOpacity={0.8} weight={3}>
          <Popup>📍 {isCitizenView ? "Your Location" : "Command Center"}</Popup>
        </CircleMarker>

        {/* Planned Route for Citizen (Dashed) if not yet responding */}
        {isCitizenView && incidents.length > 0 && 
         incidents[0].status !== 'Resolved' && 
         !ambulances.some(a => a.assigned_incident === incidents[0].id) && (
           <Polyline 
             positions={[center, [incidents[0].latitude + 0.02, incidents[0].longitude + 0.02]]} // Simulating path from nearest depot
             color="#94A3B8"
             dashArray="5, 10"
             weight={2}
             opacity={0.5}
           />
        )}

        {/* Intelligent Filtering: Only filter ambulances if a specific one is assigned to THIS citizen's incident */}
        {(isCitizenView && incidents.length > 0 && ambulances.some(a => a.assigned_incident === incidents[0].id)
           ? ambulances.filter(a => a.assigned_incident === incidents[0].id)
           : (isCitizenView ? [] : ambulances) // Show nothing if citizen hasn't been assigned yet (cleaner)
        ).map(amb => {
          const isResponding = amb.status === 'responding';
          const pos = [amb.latitude || 19.076, amb.longitude || 72.877];
          const targetInc = incidents.find(i => i.id === amb.assigned_incident);
          
          return (
            <React.Fragment key={`amb-group-${amb.id}-${amb.status}`}>
              {isResponding && targetInc && (
                <>
                  <Polyline 
                    positions={targetInc.route && targetInc.route.length > 0 
                      ? targetInc.route 
                      : [pos, [targetInc.latitude, targetInc.longitude]]
                    } 
                    color="#4F46E5" 
                    weight={6} 
                    opacity={0.3}
                    smoothFactor={1}
                  />
                  <Polyline 
                    positions={targetInc.route && targetInc.route.length > 0 
                      ? targetInc.route 
                      : [pos, [targetInc.latitude, targetInc.longitude]]
                    } 
                    color="#6366F1" 
                    dashArray="10, 15" 
                    weight={3} 
                    opacity={0.8}
                    smoothFactor={1}
                  />
                </>
              )}
              
              {isResponding && (
                <CircleMarker 
                  center={pos} 
                  radius={25} 
                  color="#6366F1" 
                  fillColor="#6366F1" 
                  fillOpacity={0.15} 
                  weight={1}
                />
              )}

              <Marker
                position={pos}
                icon={L.divIcon({
                  className: '',
                  html: `
                    <div style="position: relative; width: 44px; height: 44px;">
                      <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: ${TYPE_COLORS[amb.type?.toUpperCase()] || '#2563eb'}; border-radius: 12px; border: 2px solid #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center; transform: rotate(45deg); transition: all 0.3s ease; ${isResponding ? 'animation: pulse 1.5s infinite;' : ''}">
                        <div style="transform: rotate(-45deg); font-size: 20px;">🚑</div>
                      </div>
                      ${isResponding ? `<div style="position: absolute; top: -5px; right: -5px; width: 14px; height: 14px; background: #6366F1; border: 2px solid #fff; border-radius: 50%; z-index: 10;"></div>` : ''}
                    </div>
                  `,
                  iconSize: [44, 44],
                  iconAnchor: [22, 22],
                })}
              >
                <Popup className="custom-popup">
                  <div style={{ padding: '4px' }}>
                    <div style={{ fontSize: '14px', fontWeight: 800, color: '#1E293B' }}>{amb.id}</div>
                    <div style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', letterSpacing: '1px' }}>{amb.type} UNIT</div>
                    <div style={{ marginTop: '8px', padding: '4px 8px', background: isResponding ? '#EEF2FF' : '#F1F5F9', color: isResponding ? '#4F46E5' : '#64748B', borderRadius: '6px', fontSize: '11px', fontWeight: 700, textAlign: 'center' }}>
                      {amb.status.toUpperCase()}
                    </div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}

        {(isCitizenView && incidents.length > 0 ? incidents.slice(0, 1) : incidents)
          .filter(i => i?.latitude && i?.longitude)
          .map(inc => {
            const sev = inc.severity?.toLowerCase() || 'moderate';
            return (
              <CircleMarker
                key={`inc-${inc.id}`}
                center={[inc.latitude, inc.longitude]}
                radius={SEV_RADIUS[sev] || 10}
                color="#fff"
                fillColor={SEV_COLORS[sev] || '#ea580c'}
                fillOpacity={0.8}
                weight={3}
                style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))' }}
              >
                <Popup>
                  <div style={{ padding: '2px' }}>
                    <div style={{ color: SEV_COLORS[sev], fontWeight: 800, fontSize: '12px' }}>⚠️ {sev.toUpperCase()}</div>
                    <div style={{ fontWeight: 700, margin: '4px 0' }}>{inc.patient_name}</div>
                    <div style={{ fontSize: '11px', color: '#64748B' }}>{inc.incident_type}</div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })
        }

        {hospitals.filter(h => h?.latitude && h?.longitude).map(hosp => (
          <Marker
            key={`hosp-${hosp.id}`}
            position={[hosp.latitude, hosp.longitude]}
            icon={L.divIcon({
              className: '',
              html: `<div style="background:#10b981;width:28px;height:28px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:14px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4);">🏥</div>`,
              iconSize: [28, 28],
              iconAnchor: [14, 14],
            })}
          >
            <Popup><b>🏥 {hosp.name}</b></Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
});
LiveMap.displayName = "LiveMap";

export default LiveMap;
