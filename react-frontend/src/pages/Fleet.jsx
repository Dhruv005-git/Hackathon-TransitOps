import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { Search, Plus, Edit2, Trash2, Truck } from 'lucide-react';
import { toast, useSortableData, StatusBadge, useConfirm } from '../utils/ui';

const Fleet = () => {
  const { user } = useAuth();
  const editable = ['Admin', 'Fleet Manager'].includes(user?.role_name);
  const { confirm, Dialog: ConfirmDialog } = useConfirm();

  const [vehicles, setVehicles] = useState([]);
  const [search, setSearch]     = useState('');
  const [typeFilter, setTypeFilter]     = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [loading, setLoading]   = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    registration_no: '', model_name: '', type: 'Van',
    max_capacity_kg: 1000, odometer: 0, acquisition_cost: 500000, status: 'Available'
  });

  const fetchVehicles = async () => {
    setLoading(true);
    try {
      const res = await api.get('/vehicles/');
      setVehicles(res.data);
    } catch { toast.error('Failed to load vehicles'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchVehicles(); }, []);

  // Client-side filter + search
  const filtered = vehicles.filter(v => {
    const matchSearch = !search ||
      v.registration_no.toLowerCase().includes(search.toLowerCase()) ||
      v.model_name.toLowerCase().includes(search.toLowerCase());
    const matchType   = typeFilter   === 'All' || v.type   === typeFilter;
    const matchStatus = statusFilter === 'All' || v.status === statusFilter;
    return matchSearch && matchType && matchStatus;
  });

  const { sorted, handleSort, SortIcon } = useSortableData(filtered, 'registration_no');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) { await api.put(`/vehicles/${editingId}`, formData); toast.success('Vehicle updated'); }
      else           { await api.post('/vehicles/', formData);             toast.success('Vehicle added'); }
      setIsModalOpen(false); fetchVehicles();
    } catch (err) { toast.error(err.response?.data?.detail || 'Error saving vehicle'); }
  };

  const handleDelete = async (id) => {
    if (!(await confirm('Delete this vehicle? This cannot be undone.'))) return;
    try { await api.delete(`/vehicles/${id}`); toast.success('Vehicle deleted'); fetchVehicles(); }
    catch { toast.error('Error deleting vehicle'); }
  };

  const openAdd  = () => { setEditingId(null); setFormData({ registration_no: '', model_name: '', type: 'Van', max_capacity_kg: 1000, odometer: 0, acquisition_cost: 500000, status: 'Available' }); setIsModalOpen(true); };
  const openEdit = (v) => { setEditingId(v.id); setFormData({ ...v }); setIsModalOpen(true); };

  const counts = { total: vehicles.length, available: vehicles.filter(v=>v.status==='Available').length, onTrip: vehicles.filter(v=>v.status==='On Trip').length, inShop: vehicles.filter(v=>v.status==='In Shop').length };

  return (
    <div className="animate-fade-in">
      <ConfirmDialog />

      <div className="page-header">
        <h1 className="page-title"><Truck size={22} /> Vehicle Registry</h1>
        {editable && <button className="btn btn-primary" onClick={openAdd}><Plus size={15} /> Add Vehicle</button>}
      </div>

      {/* KPI Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Total Fleet', value: counts.total, color: 'var(--info)' },
          { label: 'Available', value: counts.available, color: 'var(--success)' },
          { label: 'On Trip', value: counts.onTrip, color: 'var(--warning)' },
          { label: 'In Shop', value: counts.inShop, color: 'var(--danger)' },
        ].map(k => (
          <div key={k.label} className="kpi-card" style={{ borderTop: `3px solid ${k.color}` }}>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-value" style={{ fontSize: '1.75rem', color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="search-wrap" style={{ flex: 1, position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input className="form-input" placeholder="Search by reg no or model…" style={{ paddingLeft: 34 }} value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="form-input" style={{ width: 140 }} value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="All">All Types</option>
          <option>Van</option><option>Truck</option><option>Mini</option>
        </select>
        <select className="form-input" style={{ width: 160 }} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="All">All Statuses</option>
          <option>Available</option><option>On Trip</option><option>In Shop</option><option>Retired</option>
        </select>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th className="sortable" onClick={() => handleSort('registration_no')}>Reg No <SortIcon k="registration_no" /></th>
              <th className="sortable" onClick={() => handleSort('model_name')}>Model <SortIcon k="model_name" /></th>
              <th className="sortable" onClick={() => handleSort('type')}>Type <SortIcon k="type" /></th>
              <th className="sortable" onClick={() => handleSort('max_capacity_kg')}>Capacity (kg) <SortIcon k="max_capacity_kg" /></th>
              <th className="sortable" onClick={() => handleSort('odometer')}>Odometer (km) <SortIcon k="odometer" /></th>
              <th>Status</th>
              {editable && <th style={{ textAlign: 'right' }}>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr className="loading-row"><td colSpan="7">Loading vehicles…</td></tr>
            ) : sorted.length === 0 ? (
              <tr><td colSpan="7" className="empty-state"><Truck size={36} /><p>No vehicles match your filters.</p></td></tr>
            ) : sorted.map(v => (
              <tr key={v.id}>
                <td style={{ fontWeight: 700, fontFamily: 'monospace' }}>{v.registration_no}</td>
                <td>{v.model_name}</td>
                <td><span className="badge badge-neutral">{v.type}</span></td>
                <td>{v.max_capacity_kg.toLocaleString()}</td>
                <td>{v.odometer.toLocaleString()}</td>
                <td><StatusBadge status={v.status} /></td>
                {editable && (
                  <td style={{ textAlign: 'right' }}>
                    <button className="btn btn-ghost" onClick={() => openEdit(v)} style={{ padding: '0.25rem 0.5rem' }}><Edit2 size={14} /></button>
                    <button className="btn btn-ghost" onClick={() => handleDelete(v.id)} style={{ padding: '0.25rem 0.5rem', color: 'var(--danger)' }}><Trash2 size={14} /></button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Showing {sorted.length} of {vehicles.length} vehicles
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsModalOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-title">{editingId ? 'Edit Vehicle' : 'Add Vehicle'}</div>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">Reg No</label><input required className="form-input" value={formData.registration_no} onChange={e => setFormData({...formData, registration_no: e.target.value})} /></div>
                <div style={{ flex: 1 }}><label className="form-label">Model</label><input required className="form-input" value={formData.model_name} onChange={e => setFormData({...formData, model_name: e.target.value})} /></div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">Type</label>
                  <select className="form-input" value={formData.type} onChange={e => setFormData({...formData, type: e.target.value})}>
                    <option>Van</option><option>Truck</option><option>Mini</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}><label className="form-label">Capacity (kg)</label><input type="number" required className="form-input" value={formData.max_capacity_kg} onChange={e => setFormData({...formData, max_capacity_kg: Number(e.target.value)})} /></div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">Odometer (km)</label><input type="number" required className="form-input" value={formData.odometer} onChange={e => setFormData({...formData, odometer: Number(e.target.value)})} /></div>
                <div style={{ flex: 1 }}><label className="form-label">Acq. Cost (₹)</label><input type="number" required className="form-input" value={formData.acquisition_cost} onChange={e => setFormData({...formData, acquisition_cost: Number(e.target.value)})} /></div>
              </div>
              <div><label className="form-label">Status</label>
                <select className="form-input" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                  <option>Available</option><option>On Trip</option><option>In Shop</option><option>Retired</option>
                </select>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Save Changes' : 'Add Vehicle'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Fleet;
