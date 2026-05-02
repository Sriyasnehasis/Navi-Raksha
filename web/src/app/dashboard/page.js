"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { db } from "../../lib/firebase";
import { collection, onSnapshot, query, orderBy, limit } from "firebase/firestore";
import { Ambulance, AlertCircle, Activity, Hospital, Clock, ChevronRight } from "lucide-react";

export default function Dashboard() {
  const [ambulances, setAmbulances] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Real-time listener for Ambulances
    const qAmb = query(collection(db, "ambulances"));
    const unsubAmb = onSnapshot(qAmb, (snapshot) => {
      setAmbulances(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
      setLoading(false);
    });

    // Real-time listener for Incidents
    const qInc = query(collection(db, "incidents"), orderBy("timestamp", "desc"), limit(10));
    const unsubInc = onSnapshot(qInc, (snapshot) => {
      setIncidents(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
    });

    return () => {
      unsubAmb();
      unsubInc();
    };
  }, []);

  return (
    <div className="container min-h-screen py-10">
      <header className="flex justify-between items-center mb-10">
        <div>
          <h2 className="brand-text text-3xl font-bold">COMMAND CENTER</h2>
          <p className="text-gray-500 text-sm">Live Dispatch Intelligence System</p>
        </div>
        <div className="flex gap-4">
          <div className="glass-card py-2 px-4 flex items-center gap-2">
            <div className="live-indicator"></div>
            <span className="text-xs font-mono">SYSTEM LIVE</span>
          </div>
        </div>
      </header>

      {/* KPI Section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div className="glass-card kpi-card">
          <div className="flex justify-between items-start mb-2">
            <Ambulance className="text-primary w-5 h-5" />
            <span className="text-xs text-green-500 font-bold">+2.4%</span>
          </div>
          <div className="kpi-value">{ambulances.length}</div>
          <div className="kpi-label">Active Units</div>
        </div>

        <div className="glass-card kpi-card">
          <div className="flex justify-between items-start mb-2">
            <AlertCircle className="text-accent w-5 h-5" />
            <span className="text-xs text-red-500 font-bold">CRITICAL</span>
          </div>
          <div className="kpi-value">{incidents.filter(i => i.status === 'waiting').length}</div>
          <div className="kpi-label">Pending Alerts</div>
        </div>

        <div className="glass-card kpi-card">
          <div className="flex justify-between items-start mb-2">
            <Clock className="text-secondary w-5 h-5" />
          </div>
          <div className="kpi-value">4.2m</div>
          <div className="kpi-label">Avg. ETA (RF)</div>
        </div>

        <div className="glass-card kpi-card">
          <div className="flex justify-between items-start mb-2">
            <Hospital className="text-primary w-5 h-5" />
          </div>
          <div className="kpi-value">92%</div>
          <div className="kpi-label">Bed Occupancy</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Incident Queue */}
        <div className="lg:col-span-1">
          <h3 className="mb-6 flex items-center gap-2">
            <Activity className="text-accent" />
            Live Feed
          </h3>
          <div className="flex flex-col gap-4">
            {incidents.map((incident) => (
              <motion.div 
                key={incident.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass-card p-4 border-l-4 border-accent"
                style={{ borderColor: incident.status === 'waiting' ? '#ff0055' : '#00f2ff' }}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="font-bold">{incident.incidentType}</span>
                  <span className="text-[10px] bg-white/10 px-2 py-1 rounded uppercase tracking-tighter">
                    {incident.status}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mb-3">Reported by: {incident.userName}</p>
                <button className="text-xs text-primary flex items-center gap-1 hover:underline">
                  Dispatch Ambulance <ChevronRight size={12} />
                </button>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Fleet Map Placeholder */}
        <div className="lg:col-span-2">
          <h3 className="mb-6 flex items-center gap-2">
            <MapPin className="text-primary" />
            Real-time Fleet Map
          </h3>
          <div className="glass-card h-[600px] flex items-center justify-center relative overflow-hidden">
             {/* Simple visual representation of a map since we can't load the full library here easily */}
             <div className="absolute inset-0 bg-blue-900/10 opacity-20 pointer-events-none">
                {/* Visual Grid */}
                <div className="w-full h-full" style={{ backgroundImage: 'radial-gradient(circle, #ffffff10 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
             </div>
             
             {ambulances.map((amb, i) => (
               <motion.div
                 key={amb.id}
                 className="absolute w-8 h-8 flex items-center justify-center"
                 initial={{ scale: 0 }}
                 animate={{ scale: 1 }}
                 style={{ 
                   left: `${(amb.longitude % 1) * 1000}%`, // Fake mapping for visual demo
                   top: `${(amb.latitude % 1) * 1000}%` 
                 }}
               >
                 <div className="relative">
                   <Ambulance className="text-primary" />
                   <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full border border-black"></div>
                 </div>
               </motion.div>
             ))}

             <div className="text-center z-10">
               <p className="text-sm text-gray-500 uppercase tracking-widest mb-2">Rendering Geospatial Grid</p>
               <h4 className="text-primary font-mono">NAVI MUMBAI SECTOR VII</h4>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MapPin({ className }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
  )
}
