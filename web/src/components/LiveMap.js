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
const SEV_COLORS  = { critical: '#dc2626', severe: '#ea580c', moderate: '#ca8a04', minor: '#16a34a' };
const SEV_RADIUS  = { critical: 14, severe: 11, moderate: 8, minor: 6 };

function MapUpdater({ center }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center);
  }, [center, map]);
  return null;
}

const LiveMap = memo(({ ambulances = [], incidents = [], hospitals = [], userLat, userLng }) => {
  const [isMounted, setIsMounted] = useState(false);
  const center = [userLat || 19.076, userLng || 72.877];

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return (
    <div style={{ width: "100%", height: "100%", background: "#f1f5f9", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "16px", color: "#94a3b8" }}>
      Initializing Map Grid...
    </div>
  );

  return (
    <div id="map-root-container" style={{ height: "100%", width: "100%", borderRadius: "16px", overflow: "hidden", border: "1px solid #E2E8F0", position: 'relative' }}>
      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
          70% { transform: scale(1.1); box-shadow: 0 0 0 15px rgba(220, 38, 38, 0); }
          100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
        }
      `}</style>
      <MapContainer 
        key="naviraksha-static-map"
        center={center} 
        zoom={13} 
        style={{ height: "100%", width: "100%", zIndex: 1 }}
        scrollWheelZoom={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        <MapUpdater center={center} />

        {/* Dynamic Data Layers */}
        <CircleMarker center={center} radius={10} color="#3b82f6" fillColor="#3b82f6" fillOpacity={0.8} weight={3}>
          <Popup>📍 Command Center</Popup>
        </CircleMarker>

        {ambulances.map(amb => {
          const isResponding = amb.status === 'responding';
          const pos = [amb.latitude || 19.076, amb.longitude || 72.877];
          const targetInc = incidents.find(i => i.id === amb.assigned_incident);
          
          return (
            <React.Fragment key={`amb-group-${amb.id}`}>
              {isResponding && targetInc && (
                <Polyline 
                  positions={[pos, [targetInc.latitude, targetInc.longitude]]} 
                  color="#4F46E5" 
                  dashArray="10, 10" 
                  weight={3} 
                  opacity={0.6}
                />
              )}
              
              {isResponding && (
                <CircleMarker 
                  center={pos} 
                  radius={20} 
                  color="#4F46E5" 
                  fillColor="#4F46E5" 
                  fillOpacity={0.1} 
                  weight={1}
                />
              )}

              <Marker
                position={pos}
                icon={L.divIcon({
                  className: '',
                  html: `<div style="background:${TYPE_COLORS[amb.type?.toUpperCase()]||'#2563eb'};width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;border:3px solid white;box-shadow:0 4px 10px rgba(0,0,0,0.15); ${isResponding ? 'animation: pulse 2s infinite;' : ''}">🚑</div>`,
                  iconSize: [32, 32],
                  iconAnchor: [16, 16],
                })}
              >
                <Popup>
                  <b>🚑 {amb.id}</b><br />
                  Status: <span style={{color: isResponding ? '#4F46E5' : '#64748b', fontWeight: 800}}>{amb.status.toUpperCase()}</span>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}

        {incidents.filter(i => i?.latitude && i?.longitude).map(inc => (
          <CircleMarker
            key={`inc-${inc.id}`}
            center={[inc.latitude, inc.longitude]}
            radius={10}
            color={inc.severity?.toLowerCase() === 'critical' ? '#dc2626' : '#ea580c'}
            fillColor={inc.severity?.toLowerCase() === 'critical' ? '#dc2626' : '#ea580c'}
            fillOpacity={0.7}
            weight={2}
          >
            <Popup><b>⚠️ {inc.patient_name}</b><br/>{inc.incident_type}</Popup>
          </CircleMarker>
        ))}

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

export default LiveMap;
