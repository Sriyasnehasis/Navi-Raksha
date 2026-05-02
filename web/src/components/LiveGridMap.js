"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { db } from "../lib/firebase";
import { collection, onSnapshot } from "firebase/firestore";

// Fix for Leaflet default icons in Next.js
const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const ambulanceIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/1066/1066915.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
});

const hospitalIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/2966/2966327.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
});

function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.setView(center, 13);
  }, [center, map]);
  return null;
}

export default function LiveGridMap({ userLocation }) {
  const [ambulances, setAmbulances] = useState([]);
  const [hospitals, setHospitals] = useState([]);

  useEffect(() => {
    // Listen for Ambulances
    const unsubAmb = onSnapshot(collection(db, "ambulances"), (snap) => {
      setAmbulances(snap.docs.map(doc => ({ id: doc.id, ...doc.data() })));
    });

    // Listen for Hospitals
    const unsubHosp = onSnapshot(collection(db, "hospitals"), (snap) => {
      setHospitals(snap.docs.map(doc => ({ id: doc.id, ...doc.data() })));
    });

    return () => {
      unsubAmb();
      unsubHosp();
    };
  }, []);

  return (
    <div className="w-full h-full rounded-2xl overflow-hidden border-2 border-[#bfdbfe] shadow-inner">
      <MapContainer 
        center={[userLocation?.lat || 19.0760, userLocation?.lng || 72.8777]} 
        zoom={13} 
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {/* User Location */}
        {userLocation?.lat && (
          <Marker position={[userLocation.lat, userLocation.lng]} icon={markerIcon}>
            <Popup>Your Current Location (Citizen)</Popup>
          </Marker>
        )}

        {/* Ambulances */}
        {ambulances.map((amb) => (
          <Marker 
            key={amb.id} 
            position={[amb.latitude, amb.longitude]} 
            icon={ambulanceIcon}
          >
            <Popup>
              <div className="font-bold">{amb.id}</div>
              <div className="text-xs uppercase text-blue-600 font-bold">{amb.status}</div>
            </Popup>
          </Marker>
        ))}

        {/* Hospitals */}
        {hospitals.map((hosp) => (
          <Marker 
            key={hosp.id} 
            position={[hosp.latitude, hosp.longitude]} 
            icon={hospitalIcon}
          >
            <Popup>
              <div className="font-bold">{hosp.name}</div>
              <div className="text-xs text-green-600 font-bold">Beds: {hosp.available_beds}</div>
            </Popup>
          </Marker>
        ))}

        <MapRecenter center={userLocation?.lat ? [userLocation.lat, userLocation.lng] : null} />
      </MapContainer>
    </div>
  );
}
