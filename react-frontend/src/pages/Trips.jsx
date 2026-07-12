import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { MapPin, Play, CheckCircle, XCircle } from 'lucide-react';

const Trips = () => {
  const { user } = useAuth();
  const editable = ['Admin', 'Dispatcher'].includes(user?.role_name);
  const isDriver = user?.role_name === 'Driver';
  
  const [trips, setTrips] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  
  const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false);
  const [activeTrip, setActiveTrip] = useState(null);
  
  const [formData, setFormData] = useState({
    trip_code: `TR-${Math.floor(Math.random()*10000)}`, source: '', destination: '',
    vehicle_id: '', driver_id: '', cargo_weight_kg: '', planned_distance_km: '', revenue: ''
  });

  const [completeData, setCompleteData] = useState({ fuel_consumed_l: '', final_odometer: '' });

  const fetchData = async () => {
    try {
      const [resTrips, resVehicles, resDrivers] = await Promise.all([
        api.get('/trips/'),
        api.get('/vehicles/'),
        api.get('/drivers/')
      ]);
      setTrips(resTrips.data);
      setVehicles(resVehicles.data);
      setDrivers(resDrivers.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/trips/', formData);
      setFormData({ trip_code: `TR-${Math.floor(Math.random()*10000)}`, source: '', destination: '', vehicle_id: '', driver_id: '', cargo_weight_kg: '', planned_distance_km: '', revenue: '' });
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error creating trip');
    }
  };

  const handleDispatch = async (id) => {
    try {
      await api.post(`/trips/${id}/dispatch`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error dispatching trip');
    }
  };

  const handleComplete = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/trips/${activeTrip.id}/complete`, completeData);
      setIsCompleteModalOpen(false);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error completing trip');
    }
  };

  const handleCancel = async (id) => {
    if(window.confirm("Cancel this trip?")) {
      try {
        await api.post(`/trips/${id}/cancel`);
        fetchData();
      } catch (err) {
        alert(err.response?.data?.detail || 'Error cancelling trip');
      }
    }
  };

  const statusColor = (s) =>
    s === 'Completed' ? 'var(--success)' :
    s === 'Dispatched' ? 'var(--info)' :
    s === 'Cancelled' ? 'var(--danger)' : 'var(--warning)';

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <MapPin size={24} color="var(--primary)" />
          {isDriver ? 'My Trips' : 'Trip Dispatching'}
        </h1>
      </div>

      {/* ── DRIVER VIEW: read-only card grid ── */}
      {isDriver ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1rem' }}>
          {trips.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No trips found.</p>}
          {trips.map(t => (
            <div key={t.id} className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', borderLeft: `4px solid ${statusColor(t.status)}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 700, fontSize: '1.125rem' }}>{t.trip_code}</span>
                <span style={{ padding: '4px 12px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, background: statusColor(t.status), color: 'white' }}>{t.status}</span>
              </div>
              <div style={{ fontSize: '0.9375rem' }}>
                {t.source} <span style={{ color: 'var(--text-muted)', margin: '0 0.5rem' }}>➔</span> {t.destination}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                <span>🚛 {t.vehicle?.registration_no}</span>
                <span>👤 {t.driver?.name}</span>
                <span>⚖️ {t.cargo_weight_kg} kg</span>
                <span>📏 {t.planned_distance_km} km</span>
              </div>
            </div>
          ))}
        </div>

      ) : (
        /* ── DISPATCHER / ADMIN VIEW: split-screen ── */
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2.5rem', flex: 1 }}>

          {/* Left: Create Trip Form */}
          <div className="card" style={{ padding: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>NEW TRIP DISPATCH</h3>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">SOURCE</label><input required className="form-input" value={formData.source} onChange={e => setFormData({...formData, source: e.target.value})} disabled={!editable} /></div>
                <div style={{ flex: 1 }}><label className="form-label">DESTINATION</label><input required className="form-input" value={formData.destination} onChange={e => setFormData({...formData, destination: e.target.value})} disabled={!editable} /></div>
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <label className="form-label">VEHICLE (AVAILABLE ONLY)</label>
                  <select required className="form-input" value={formData.vehicle_id} onChange={e => setFormData({...formData, vehicle_id: Number(e.target.value)})} disabled={!editable}>
                    <option value="">Select...</option>
                    {vehicles.filter(v => v.status === 'Available').map(v => <option key={v.id} value={v.id}>{v.registration_no} ({v.max_capacity_kg}kg)</option>)}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label className="form-label">DRIVER (AVAILABLE ONLY)</label>
                  <select required className="form-input" value={formData.driver_id} onChange={e => setFormData({...formData, driver_id: Number(e.target.value)})} disabled={!editable}>
                    <option value="">Select...</option>
                    {drivers.filter(d => d.status === 'Available').map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">CARGO WEIGHT (KG)</label><input type="number" required className="form-input" value={formData.cargo_weight_kg} onChange={e => setFormData({...formData, cargo_weight_kg: Number(e.target.value)})} disabled={!editable} /></div>
                <div style={{ flex: 1 }}><label className="form-label">PLANNED DISTANCE (KM)</label><input type="number" required className="form-input" value={formData.planned_distance_km} onChange={e => setFormData({...formData, planned_distance_km: Number(e.target.value)})} disabled={!editable} /></div>
                <div style={{ flex: 1 }}><label className="form-label">EST. REVENUE (₹)</label><input type="number" required className="form-input" value={formData.revenue} onChange={e => setFormData({...formData, revenue: Number(e.target.value)})} disabled={!editable} /></div>
              </div>

              {editable && (
                <div style={{ marginTop: '1.5rem' }}>
                  <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>Create Draft</button>
                </div>
              )}
            </form>
          </div>

          {/* Right: Live Board */}
          <div>
            <h3 style={{ marginBottom: '1.5rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>LIVE BOARD (ACTIVE TRIPS)</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '70vh', overflowY: 'auto', paddingRight: '1rem' }}>
              {trips.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No trips found.</p>}
              {trips.map(t => (
                <div key={t.id} className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', borderLeft: `4px solid ${statusColor(t.status)}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, fontSize: '1.125rem' }}>{t.trip_code}</span>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{t.vehicle?.registration_no} • {t.driver?.name}</span>
                  </div>
                  <div style={{ fontSize: '0.9375rem' }}>
                    {t.source} <span style={{ color: 'var(--text-muted)', margin: '0 0.5rem' }}>➔</span> {t.destination}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                    <span style={{ padding: '4px 12px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, background: statusColor(t.status), color: 'white' }}>{t.status}</span>
                    {editable && (
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {t.status === 'Draft' && (
                          <>
                            <button className="btn btn-ghost" onClick={() => handleDispatch(t.id)} style={{ padding: '0.25rem 0.75rem', color: 'var(--info)', border: '1px solid var(--info)' }}>Dispatch</button>
                            <button className="btn btn-ghost" onClick={() => handleCancel(t.id)} style={{ padding: '0.25rem 0.75rem', color: 'var(--danger)', border: '1px solid var(--danger)' }}>Cancel</button>
                          </>
                        )}
                        {t.status === 'Dispatched' && (
                          <button className="btn btn-ghost" onClick={() => { setActiveTrip(t); setCompleteData({ fuel_consumed_l: '', final_odometer: t.vehicle?.odometer || '' }); setIsCompleteModalOpen(true); }} style={{ padding: '0.25rem 0.75rem', color: 'var(--success)', border: '1px solid var(--success)' }}>Complete</button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {/* Complete Trip Modal */}
      {isCompleteModalOpen && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '1rem', backdropFilter: 'blur(4px)' }}>
          <div className="card animate-fade-in" style={{ width: '100%', maxWidth: '440px' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Complete Trip {activeTrip?.trip_code}</h2>
            <form onSubmit={handleComplete} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label className="form-label">Fuel Consumed (Liters)</label>
                <input type="number" step="0.1" required className="form-input" value={completeData.fuel_consumed_l} onChange={e => setCompleteData({...completeData, fuel_consumed_l: Number(e.target.value)})} />
              </div>
              <div>
                <label className="form-label">Final Odometer</label>
                <input type="number" step="0.1" required className="form-input" value={completeData.final_odometer} onChange={e => setCompleteData({...completeData, final_odometer: Number(e.target.value)})} />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-ghost" onClick={() => setIsCompleteModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: 'var(--success)', color: 'white' }}>Complete Trip</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Trips;
