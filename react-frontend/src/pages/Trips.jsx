import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { MapPin, Play, CheckCircle, XCircle, Truck, User, Scale, Navigation, IndianRupee, Calendar } from 'lucide-react';
import { toast } from '../utils/ui';

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
      toast.error('Failed to load trips data');
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
      toast.success('Trip created successfully');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error creating trip');
    }
  };

  const [loadingAction, setLoadingAction] = useState(null);

  const handleDispatch = async (id) => {
    setLoadingAction(`dispatch-${id}`);
    try {
      await api.post(`/trips/${id}/dispatch`);
      toast.success('Trip dispatched');
      await fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error dispatching trip');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleComplete = async (e) => {
    e.preventDefault();
    setLoadingAction(`complete-${activeTrip.id}`);
    try {
      await api.post(`/trips/${activeTrip.id}/complete`, completeData);
      setIsCompleteModalOpen(false);
      toast.success('Trip marked as completed');
      await fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error completing trip');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleCancel = async (id) => {
    if(window.confirm("Are you sure you want to cancel this trip?")) {
      setLoadingAction(`cancel-${id}`);
      try {
        await api.post(`/trips/${id}/cancel`);
        toast.info('Trip cancelled');
        await fetchData();
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Error cancelling trip');
      } finally {
        setLoadingAction(null);
      }
    }
  };

  const getBadgeClass = (status) => {
    switch (status) {
      case 'Completed': return 'badge badge-success';
      case 'Dispatched': return 'badge badge-info';
      case 'Cancelled': return 'badge badge-danger';
      default: return 'badge badge-warning';
    }
  };

  const statusColor = (status) => {
    switch (status) {
      case 'Completed': return 'var(--success)';
      case 'Dispatched': return 'var(--info)';
      case 'Cancelled': return 'var(--danger)';
      default: return 'var(--warning)';
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="page-header">
        <h1 style={{ margin: 0, fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'var(--primary-light)', padding: '0.5rem', borderRadius: '8px', color: 'var(--primary)' }}>
            <MapPin size={24} />
          </div>
          {isDriver ? 'My Trips' : 'Trip Dispatching'}
        </h1>
      </div>

      {/* ── DRIVER VIEW: read-only card grid ── */}
      {isDriver ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.5rem', marginTop: '1rem' }}>
          {trips.length === 0 && <div className="empty-state">No trips assigned to you yet.</div>}
          {trips.map(t => (
            <div key={t.id} className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', borderTop: `4px solid ${statusColor(t.status)}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--primary)' }}>{t.trip_code}</span>
                <span className={getBadgeClass(t.status)}>{t.status}</span>
              </div>
              
              <div style={{ padding: '1rem', background: 'var(--background)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', fontWeight: 600 }}>SOURCE</div>
                  <div style={{ fontWeight: 600 }}>{t.source}</div>
                </div>
                <div style={{ color: 'var(--primary)', opacity: 0.5 }}>
                  <Navigation size={20} />
                </div>
                <div style={{ flex: 1, textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', fontWeight: 600 }}>DESTINATION</div>
                  <div style={{ fontWeight: 600 }}>{t.destination}</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Truck size={16} color="var(--primary)"/> {t.vehicle?.registration_no}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><User size={16} color="var(--primary)"/> {t.driver?.name}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Scale size={16} color="var(--primary)"/> {t.cargo_weight_kg} kg</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><MapPin size={16} color="var(--primary)"/> {t.planned_distance_km} km</div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* ── DISPATCHER / ADMIN / READ-ONLY VIEW ── */
        <div style={{ display: 'grid', gridTemplateColumns: editable ? 'minmax(350px, 1fr) 1fr' : '1fr', gap: '2rem', flex: 1, alignItems: 'start' }}>

          {/* Left: Create Trip Form (Only for editable roles) */}
          {editable && (
            <div className="card" style={{ padding: '2rem' }}>
              <div className="section-label" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Navigation size={18} />
                NEW TRIP DISPATCH
              </div>
              
              <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                
                {/* Route */}
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <div style={{ flex: 1 }}>
                    <label className="form-label">SOURCE LOCATION</label>
                    <input required className="form-input" placeholder="e.g. Mumbai Hub" value={formData.source} onChange={e => setFormData({...formData, source: e.target.value})} disabled={!editable} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <label className="form-label">DESTINATION LOCATION</label>
                    <input required className="form-input" placeholder="e.g. Pune Depot" value={formData.destination} onChange={e => setFormData({...formData, destination: e.target.value})} disabled={!editable} />
                  </div>
                </div>

                {/* Assignment */}
                <div style={{ display: 'flex', gap: '1rem', background: 'var(--bg-base)', padding: '1rem', borderRadius: '8px' }}>
                  <div style={{ flex: 1 }}>
                    <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Truck size={14}/> VEHICLE (AVAILABLE)</label>
                    <select required className="form-input" value={formData.vehicle_id} onChange={e => setFormData({...formData, vehicle_id: Number(e.target.value)})} disabled={!editable}>
                      <option value="">-- Assign Vehicle --</option>
                      {vehicles.filter(v => v.status === 'Available').map(v => <option key={v.id} value={v.id}>{v.registration_no} ({v.max_capacity_kg}kg)</option>)}
                    </select>
                  </div>
                  <div style={{ flex: 1 }}>
                    <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><User size={14}/> DRIVER (AVAILABLE)</label>
                    <select required className="form-input" value={formData.driver_id} onChange={e => setFormData({...formData, driver_id: Number(e.target.value)})} disabled={!editable}>
                      <option value="">-- Assign Driver --</option>
                      {drivers.filter(d => d.status === 'Available').map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                    </select>
                  </div>
                </div>

                {/* Specs */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                  <div>
                    <label className="form-label">CARGO (KG)</label>
                    <div style={{ position: 'relative' }}>
                      <div style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}><Scale size={16} /></div>
                      <input type="number" required className="form-input" style={{ paddingLeft: '2.5rem' }} placeholder="0" value={formData.cargo_weight_kg} onChange={e => setFormData({...formData, cargo_weight_kg: Number(e.target.value)})} disabled={!editable} />
                    </div>
                  </div>
                  <div>
                    <label className="form-label">DISTANCE (KM)</label>
                    <div style={{ position: 'relative' }}>
                      <div style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}><MapPin size={16} /></div>
                      <input type="number" required className="form-input" style={{ paddingLeft: '2.5rem' }} placeholder="0" value={formData.planned_distance_km} onChange={e => setFormData({...formData, planned_distance_km: Number(e.target.value)})} disabled={!editable} />
                    </div>
                  </div>
                  <div>
                    <label className="form-label">REVENUE (₹)</label>
                    <div style={{ position: 'relative' }}>
                      <div style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}><IndianRupee size={16} /></div>
                      <input type="number" required className="form-input" style={{ paddingLeft: '2.5rem' }} placeholder="0" value={formData.revenue} onChange={e => setFormData({...formData, revenue: Number(e.target.value)})} disabled={!editable} />
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: '0.5rem' }}>
                  <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.875rem', fontSize: '1rem' }} disabled={loadingAction}>
                    {loadingAction ? 'Creating...' : 'Create & Save Draft'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Right: Live Board */}
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="section-label" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Calendar size={18} />
              LIVE BOARD
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, overflowY: 'auto', maxHeight: 'calc(100vh - 220px)', paddingRight: '0.5rem', paddingBottom: '2rem' }} className="custom-scrollbar">
              {trips.length === 0 && <div className="empty-state">No active or historical trips found.</div>}
              
              {trips.map(t => (
                <div key={t.id} className="card" style={{ 
                  padding: '1.25rem 1.5rem', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  gap: '0.75rem',
                  borderLeft: `4px solid ${statusColor(t.status)}`,
                  transition: 'all 0.2s',
                  cursor: 'default',
                  flexShrink: 0
                }}>
                  {/* Top Row: Title, Driver, Badge */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <span style={{ fontWeight: 800, fontSize: '1.125rem', letterSpacing: '0.5px' }}>{t.trip_code}</span>
                      <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Truck size={14} /> {t.vehicle?.registration_no} &bull; <User size={14} /> {t.driver?.name}
                      </span>
                    </div>
                    <span className={getBadgeClass(t.status)}>{t.status}</span>
                  </div>
                  
                  {/* Middle Row: Route */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', background: 'var(--bg-base)', borderRadius: '6px' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9375rem', flex: 1, textAlign: 'right' }}>{t.source}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--primary)', opacity: 0.6 }}>
                       <div style={{ height: '2px', width: '20px', background: 'currentColor', borderRadius: '2px' }}></div>
                       <Play size={14} fill="currentColor" />
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '0.9375rem', flex: 1 }}>{t.destination}</div>
                  </div>
                  
                  {/* Bottom Row: Actions */}
                  {editable && (t.status === 'Draft' || t.status === 'Dispatched') && (
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '0.25rem' }}>
                      {t.status === 'Draft' && (
                        <>
                          <button className="btn btn-ghost" onClick={() => handleCancel(t.id)} style={{ color: 'var(--danger)' }}>
                            <XCircle size={16} /> Cancel
                          </button>
                          <button className="btn" onClick={() => handleDispatch(t.id)} style={{ background: 'var(--info)', color: 'white' }}>
                            <Navigation size={16} /> Dispatch
                          </button>
                        </>
                      )}
                      {t.status === 'Dispatched' && (
                        <button className="btn" onClick={() => { setActiveTrip(t); setCompleteData({ fuel_consumed_l: '', final_odometer: t.vehicle?.odometer || '' }); setIsCompleteModalOpen(true); }} style={{ background: 'var(--success)', color: 'white' }}>
                          <CheckCircle size={16} /> Mark Complete
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {/* Complete Trip Modal */}
      {isCompleteModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-box">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', color: 'var(--success)' }}>
              <CheckCircle size={28} />
              <h2 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--text)' }}>Complete Trip {activeTrip?.trip_code}</h2>
            </div>
            
            <form onSubmit={handleComplete} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label className="form-label">Fuel Consumed (Liters)</label>
                <input type="number" step="0.1" required className="form-input" placeholder="e.g. 45.5" value={completeData.fuel_consumed_l} onChange={e => setCompleteData({...completeData, fuel_consumed_l: Number(e.target.value)})} autoFocus />
              </div>
              <div>
                <label className="form-label">Final Odometer Reading</label>
                <input type="number" step="0.1" required className="form-input" placeholder="e.g. 24500" value={completeData.final_odometer} onChange={e => setCompleteData({...completeData, final_odometer: Number(e.target.value)})} />
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
                <button type="button" className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }} onClick={() => setIsCompleteModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1, justifyContent: 'center', background: 'var(--success)' }}>Submit & Close</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Trips;
