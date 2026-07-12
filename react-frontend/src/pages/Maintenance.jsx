import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { Plus, CheckCircle, Wrench } from 'lucide-react';
import { toast, useSortableData, StatusBadge, useConfirm } from '../utils/ui';

const Maintenance = () => {
  const { user } = useAuth();
  const editable = ['Admin', 'Fleet Manager'].includes(user?.role_name);
  const { confirm, Dialog: ConfirmDialog } = useConfirm();

  const [logs, setLogs]       = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [vehicleFilter, setVehicleFilter] = useState('All');
  const [statusFilter, setStatusFilter]   = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const today = new Date().toISOString().split('T')[0];
  const [formData, setFormData] = useState({ vehicle_id: '', service_type: 'Oil Change', cost: '', date: today });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resLogs, resVeh] = await Promise.all([api.get('/maintenance/'), api.get('/vehicles/')]);
      setLogs(resLogs.data); setVehicles(resVeh.data);
    } catch { toast.error('Failed to load maintenance data'); }
    finally { setLoading(false); }
  };
  useEffect(() => { fetchData(); }, []);

  const filtered = logs.filter(log => {
    const matchVehicle = vehicleFilter === 'All' || String(log.vehicle_id) === vehicleFilter;
    const matchStatus  = statusFilter  === 'All' || log.status === statusFilter;
    return matchVehicle && matchStatus;
  });
  const { sorted, handleSort, SortIcon } = useSortableData(filtered, 'date', 'desc');

  const handleCreate = async (e) => {
    e.preventDefault();
    try { await api.post('/maintenance/', formData); toast.success('Maintenance log created'); setIsModalOpen(false); fetchData(); }
    catch (err) { toast.error(err.response?.data?.detail || 'Error logging maintenance'); }
  };

  const handleClose = async (id) => {
    if (!(await confirm('Mark this maintenance as Completed? The vehicle will be set back to Available.'))) return;
    try { await api.post(`/maintenance/${id}/close`); toast.success('Maintenance completed'); fetchData(); }
    catch (err) { toast.error(err.response?.data?.detail || 'Error closing log'); }
  };

  const totalCost = filtered.reduce((s, l) => s + (l.cost || 0), 0);

  return (
    <div className="animate-fade-in">
      <ConfirmDialog />

      <div className="page-header">
        <h1 className="page-title"><Wrench size={22} /> Maintenance Logs</h1>
        {editable && <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}><Plus size={15} /> Add Log</button>}
      </div>

      {/* KPI Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Total Logs', value: logs.length, color: 'var(--info)' },
          { label: 'Active', value: logs.filter(l => l.status === 'Active').length, color: 'var(--danger)' },
          { label: 'Total Cost', value: `₹${logs.reduce((s,l) => s+l.cost, 0).toLocaleString()}`, color: 'var(--warning)' },
        ].map(k => (
          <div key={k.label} className="kpi-card" style={{ borderTop: `3px solid ${k.color}` }}>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <select className="form-input" style={{ width: 200 }} value={vehicleFilter} onChange={e => setVehicleFilter(e.target.value)}>
          <option value="All">All Vehicles</option>
          {vehicles.map(v => <option key={v.id} value={String(v.id)}>{v.registration_no}</option>)}
        </select>
        <select className="form-input" style={{ width: 160 }} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="All">All Statuses</option>
          <option>Active</option><option>Completed</option>
        </select>
        <div style={{ marginLeft: 'auto', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Filtered cost: <strong style={{ color: 'var(--warning)' }}>₹{totalCost.toLocaleString()}</strong>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th className="sortable" onClick={() => handleSort('date')}>Date <SortIcon k="date" /></th>
              <th>Vehicle</th>
              <th>Service Type</th>
              <th className="sortable" onClick={() => handleSort('cost')}>Cost (₹) <SortIcon k="cost" /></th>
              <th>Status</th>
              {editable && <th style={{ textAlign: 'right' }}>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr className="loading-row"><td colSpan="6">Loading logs…</td></tr>
            ) : sorted.length === 0 ? (
              <tr><td colSpan="6"><div className="empty-state"><Wrench size={36} /><p>No maintenance logs found.</p></div></td></tr>
            ) : sorted.map(log => (
              <tr key={log.id}>
                <td style={{ fontWeight: 500 }}>{log.date}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{log.vehicle?.registration_no}</td>
                <td>{log.service_type}</td>
                <td style={{ fontWeight: 600 }}>₹{log.cost.toLocaleString()}</td>
                <td><StatusBadge status={log.status} /></td>
                {editable && (
                  <td style={{ textAlign: 'right' }}>
                    {log.status === 'Active' && (
                      <button className="btn btn-ghost" onClick={() => handleClose(log.id)} style={{ padding: '0.25rem 0.5rem', color: 'var(--success)', fontSize: '0.8rem', gap: '0.3rem' }}>
                        <CheckCircle size={14} /> Complete
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>Showing {sorted.length} of {logs.length} logs</div>

      {isModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsModalOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Log Maintenance</div>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div><label className="form-label">Vehicle</label>
                <select required className="form-input" value={formData.vehicle_id} onChange={e => setFormData({...formData, vehicle_id: Number(e.target.value)})}>
                  <option value="">Select vehicle…</option>
                  {vehicles.filter(v => v.status !== 'Retired' && v.status !== 'On Trip').map(v => <option key={v.id} value={v.id}>{v.registration_no} — {v.model_name}</option>)}
                </select>
              </div>
              <div><label className="form-label">Service Type</label>
                <select required className="form-input" value={formData.service_type} onChange={e => setFormData({...formData, service_type: e.target.value})}>
                  <option>Oil Change</option><option>Tyre Replacement</option><option>Engine Tuning</option><option>Accident Repair</option><option>Brake Service</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">Cost (₹)</label><input type="number" required className="form-input" value={formData.cost} onChange={e => setFormData({...formData, cost: Number(e.target.value)})} /></div>
                <div style={{ flex: 1 }}><label className="form-label">Date</label><input type="date" required className="form-input" value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} /></div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Log</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Maintenance;
