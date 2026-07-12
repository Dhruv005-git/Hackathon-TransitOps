import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity, Truck, Wrench, MapPin, Clock, Users, TrendingUp, ChevronRight, IndianRupee } from 'lucide-react';
import { StatusBadge } from '../utils/ui';
import { useNavigate } from 'react-router-dom';

const KpiCard = ({ label, value, icon, color, sub }) => (
  <div className="kpi-card" style={{ borderTop: `3px solid ${color}` }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div className="kpi-label">{label}</div>
      <div style={{ color, opacity: 0.7 }}>{icon}</div>
    </div>
    <div className="kpi-value" style={{ color }}>{value}</div>
    {sub && <div className="kpi-sub">{sub}</div>}
  </div>
);

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [filters, setFilters] = useState({ vehicle_type: 'All', status: 'All' });
  const [kpis, setKpis] = useState(null);
  const [recentTrips, setRecentTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const params = {};
      if (filters.vehicle_type !== 'All') params.vehicle_type = filters.vehicle_type;
      if (filters.status       !== 'All') params.status       = filters.status;
      const [resKpi, resTrips] = await Promise.all([
        api.get('/analytics/kpis', { params }),
        api.get('/trips/')
      ]);
      setKpis(resKpi.data);
      setRecentTrips(resTrips.data.slice(0, 6));
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [filters]);

  if (loading) return <div style={{ padding: '2rem', color: 'var(--text-muted)', textAlign: 'center' }}>Loading dashboard…</div>;
  if (!kpis) return null;

  const vehicleStatusData = [
    { name: 'Available', count: kpis.available_vehicles, color: '#10b981' },
    { name: 'On Trip',   count: kpis.active_vehicles,    color: '#3b82f6' },
    { name: 'In Shop',   count: kpis.in_shop_vehicles,   color: '#ef4444' },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

      {/* Header + Filters */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.04em', margin: 0 }}>Overview</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: '0.25rem 0 0' }}>Welcome back, <strong>{user?.name}</strong> — {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <select className="form-input" style={{ width: 150 }} value={filters.vehicle_type} onChange={e => setFilters({...filters, vehicle_type: e.target.value})}>
            <option value="All">All Types</option>
            <option value="Truck">Trucks</option>
            <option value="Van">Vans</option>
            <option value="Mini">Minis</option>
          </select>
          <select className="form-input" style={{ width: 155 }} value={filters.status} onChange={e => setFilters({...filters, status: e.target.value})}>
            <option value="All">All Statuses</option>
            <option value="Available">Available</option>
            <option value="On Trip">On Trip</option>
            <option value="In Shop">In Shop</option>
          </select>
        </div>
      </div>

      {/* KPI Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.875rem' }}>
        <KpiCard label="Active Vehicles"  value={kpis.active_vehicles}    icon={<Truck size={18} />}     color="var(--info)"    />
        <KpiCard label="Available"        value={kpis.available_vehicles} icon={<Activity size={18} />}  color="var(--success)" />
        <KpiCard label="In Maintenance"   value={kpis.in_shop_vehicles}   icon={<Wrench size={18} />}    color="var(--danger)"  />
        <KpiCard label="Active Trips"     value={kpis.active_trips}       icon={<MapPin size={18} />}    color="var(--info)"    />
        <KpiCard label="Pending Trips"    value={kpis.pending_trips}      icon={<Clock size={18} />}     color="var(--warning)" />
        <KpiCard label="Drivers On Duty"  value={kpis.drivers_on_duty}    icon={<Users size={18} />}     color="#8b5cf6"        />
        <KpiCard label="Fleet Util."      value={`${kpis.utilization_percent?.toFixed(1)}%`} icon={<TrendingUp size={18} />} color="var(--accent)" />
        <KpiCard label="Total Revenue"    value={`₹${(kpis.total_revenue || 0).toLocaleString()}`} icon={<IndianRupee size={18} />} color="var(--success)" />
      </div>

      {/* Bottom Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>

        {/* Recent Trips */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ margin: 0, fontSize: '0.9375rem', fontWeight: 600 }}>Recent Trips</h3>
            <button className="btn btn-ghost" style={{ fontSize: '0.8rem', padding: '0.25rem 0.75rem' }} onClick={() => navigate('/trips')}>
              View All <ChevronRight size={14} />
            </button>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Trip Code</th>
                <th>Route</th>
                <th>Vehicle</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentTrips.map(t => (
                <tr key={t.id} style={{ cursor: 'pointer' }} onClick={() => navigate('/trips')}>
                  <td style={{ fontWeight: 700, fontFamily: 'monospace', fontSize: '0.85rem' }}>{t.trip_code}</td>
                  <td style={{ fontSize: '0.875rem' }}>{t.source} <span style={{ color: 'var(--text-muted)' }}>→</span> {t.destination}</td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{t.vehicle?.registration_no}</td>
                  <td><StatusBadge status={t.status} /></td>
                </tr>
              ))}
              {recentTrips.length === 0 && (
                <tr><td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>No trips yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Vehicle Status Chart */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1.25rem', fontSize: '0.9375rem', fontWeight: 600 }}>Vehicle Status</h3>
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={vehicleStatusData} margin={{ top: 0, right: 40, left: 0, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} width={75} />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '8px', fontSize: '0.85rem' }} />
                <Bar dataKey="count" radius={[0, 5, 5, 0]} maxBarSize={28} label={{ position: 'right', fill: 'var(--text-primary)', fontSize: 13, fontWeight: 700 }}>
                  {vehicleStatusData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="divider" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {vehicleStatusData.map(d => (
              <div key={d.name} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: d.color, display: 'inline-block' }} />
                  {d.name}
                </span>
                <span style={{ fontWeight: 600, color: d.color }}>{d.count}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
