import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { Search, Plus, Edit2, Trash2, Users, AlertTriangle } from 'lucide-react';
import { toast, useSortableData, StatusBadge, useConfirm } from '../utils/ui';

const ScoreBar = ({ score }) => {
  const color = score >= 85 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--danger)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <div className="progress-bar" style={{ width: 60 }}>
        <div className="progress-bar-fill" style={{ width: `${score}%`, background: color }} />
      </div>
      <span style={{ fontSize: '0.8rem', color, fontWeight: 600 }}>{score}</span>
    </div>
  );
};

const Drivers = () => {
  const { user } = useAuth();
  const editable = ['Admin', 'Fleet Manager', 'Safety Officer'].includes(user?.role_name);
  const { confirm, Dialog: ConfirmDialog } = useConfirm();

  const [drivers, setDrivers]     = useState([]);
  const [search, setSearch]       = useState('');
  const [statusFilter, setStatusFilter]   = useState('All');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [loading, setLoading]     = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const today = new Date().toISOString().split('T')[0];
  const nextYear = () => { const d = new Date(); d.setFullYear(d.getFullYear()+1); return d.toISOString().split('T')[0]; };
  const [formData, setFormData]   = useState({ name: '', license_no: '', license_category: 'LMV', license_expiry: nextYear(), contact_no: '', safety_score: 100, status: 'Available' });

  const fetchDrivers = async () => {
    setLoading(true);
    try { const res = await api.get('/drivers/'); setDrivers(res.data); }
    catch { toast.error('Failed to load drivers'); }
    finally { setLoading(false); }
  };
  useEffect(() => { fetchDrivers(); }, []);

  const filtered = drivers.filter(d => {
    const matchSearch = !search || d.name.toLowerCase().includes(search.toLowerCase()) || d.license_no.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'All' || d.status === statusFilter;
    const matchCat    = categoryFilter === 'All' || d.license_category === categoryFilter;
    return matchSearch && matchStatus && matchCat;
  });

  const { sorted, handleSort, SortIcon } = useSortableData(filtered, 'name');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) { await api.put(`/drivers/${editingId}`, formData); toast.success('Driver updated'); }
      else           { await api.post('/drivers/', formData);             toast.success('Driver added'); }
      setIsModalOpen(false); fetchDrivers();
    } catch (err) { toast.error(err.response?.data?.detail || 'Error saving driver'); }
  };

  const handleDelete = async (id) => {
    if (!(await confirm('Delete this driver profile?'))) return;
    try { await api.delete(`/drivers/${id}`); toast.success('Driver deleted'); fetchDrivers(); }
    catch { toast.error('Error deleting driver'); }
  };

  const openAdd  = () => { setEditingId(null); setFormData({ name: '', license_no: '', license_category: 'LMV', license_expiry: nextYear(), contact_no: '', safety_score: 100, status: 'Available' }); setIsModalOpen(true); };
  const openEdit = (d) => { setEditingId(d.id); setFormData({ ...d }); setIsModalOpen(true); };

  const expiredCount = drivers.filter(d => d.license_expiry < today).length;
  const expiringCount = drivers.filter(d => d.license_expiry >= today && d.license_expiry <= new Date(Date.now() + 30*86400000).toISOString().split('T')[0]).length;

  return (
    <div className="animate-fade-in">
      <ConfirmDialog />

      <div className="page-header">
        <h1 className="page-title"><Users size={22} /> Driver Management</h1>
        {editable && <button className="btn btn-primary" onClick={openAdd}><Plus size={15} /> Add Driver</button>}
      </div>

      {/* KPI Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Total', value: drivers.length, color: 'var(--info)' },
          { label: 'Available', value: drivers.filter(d=>d.status==='Available').length, color: 'var(--success)' },
          { label: 'On Trip', value: drivers.filter(d=>d.status==='On Trip').length, color: 'var(--warning)' },
          { label: 'Suspended', value: drivers.filter(d=>d.status==='Suspended').length, color: 'var(--danger)' },
          { label: 'Expired License', value: expiredCount, color: 'var(--danger)' },
        ].map(k => (
          <div key={k.label} className="kpi-card" style={{ borderTop: `3px solid ${k.color}` }}>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-value" style={{ fontSize: '1.75rem', color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {expiringCount > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.875rem 1.25rem', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: '8px', marginBottom: '1.25rem', fontSize: '0.875rem', color: 'var(--warning)' }}>
          <AlertTriangle size={16} />
          <strong>{expiringCount} driver{expiringCount > 1 ? 's' : ''}</strong> have a license expiring within 30 days.
        </div>
      )}

      {/* Filter Bar */}
      <div className="filter-bar">
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input className="form-input" placeholder="Search name or license no…" style={{ paddingLeft: 34 }} value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="form-input" style={{ width: 150 }} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="All">All Statuses</option>
          <option>Available</option><option>On Trip</option><option>Off Duty</option><option>Suspended</option>
        </select>
        <select className="form-input" style={{ width: 140 }} value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
          <option value="All">All Categories</option>
          <option>LMV</option><option>HMV</option>
        </select>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th className="sortable" onClick={() => handleSort('name')}>Name <SortIcon k="name" /></th>
              <th>License No</th>
              <th>Category</th>
              <th className="sortable" onClick={() => handleSort('license_expiry')}>Expiry <SortIcon k="license_expiry" /></th>
              <th>Contact</th>
              <th className="sortable" onClick={() => handleSort('safety_score')}>Safety Score <SortIcon k="safety_score" /></th>
              <th>Status</th>
              {editable && <th style={{ textAlign: 'right' }}>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr className="loading-row"><td colSpan="8">Loading drivers…</td></tr>
            ) : sorted.length === 0 ? (
              <tr><td colSpan="8"><div className="empty-state"><Users size={36} /><p>No drivers match your filters.</p></div></td></tr>
            ) : sorted.map(d => {
              const isExpired  = d.license_expiry < today;
              const isExpiring = !isExpired && d.license_expiry <= new Date(Date.now() + 30*86400000).toISOString().split('T')[0];
              return (
                <tr key={d.id} className={isExpired ? 'row-danger' : isExpiring ? 'row-warning' : ''}>
                  <td style={{ fontWeight: 600 }}>{d.name}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{d.license_no}</td>
                  <td><span className="badge badge-neutral">{d.license_category}</span></td>
                  <td>
                    {isExpired   && <span style={{ color: 'var(--danger)', fontWeight: 600, fontSize: '0.8rem' }}>⚠ {d.license_expiry}</span>}
                    {isExpiring  && <span style={{ color: 'var(--warning)', fontWeight: 600, fontSize: '0.8rem' }}>⏰ {d.license_expiry}</span>}
                    {!isExpired && !isExpiring && <span style={{ fontSize: '0.85rem' }}>{d.license_expiry}</span>}
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{d.contact_no}</td>
                  <td><ScoreBar score={d.safety_score} /></td>
                  <td><StatusBadge status={d.status} /></td>
                  {editable && (
                    <td style={{ textAlign: 'right' }}>
                      <button className="btn btn-ghost" onClick={() => openEdit(d)} style={{ padding: '0.25rem 0.5rem' }}><Edit2 size={14} /></button>
                      <button className="btn btn-ghost" onClick={() => handleDelete(d.id)} style={{ padding: '0.25rem 0.5rem', color: 'var(--danger)' }}><Trash2 size={14} /></button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>Showing {sorted.length} of {drivers.length} drivers</div>

      {isModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsModalOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-title">{editingId ? 'Edit Driver' : 'Add Driver'}</div>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">Full Name</label><input required className="form-input" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} /></div>
                <div style={{ flex: 1 }}><label className="form-label">Contact No</label><input required className="form-input" value={formData.contact_no} onChange={e => setFormData({...formData, contact_no: e.target.value})} /></div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">License No</label><input required className="form-input" value={formData.license_no} onChange={e => setFormData({...formData, license_no: e.target.value})} /></div>
                <div style={{ flex: 1 }}><label className="form-label">Category</label>
                  <select className="form-input" value={formData.license_category} onChange={e => setFormData({...formData, license_category: e.target.value})}>
                    <option>LMV</option><option>HMV</option>
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">License Expiry</label><input type="date" required className="form-input" value={formData.license_expiry} onChange={e => setFormData({...formData, license_expiry: e.target.value})} /></div>
                <div style={{ flex: 1 }}><label className="form-label">Safety Score (0–100)</label><input type="number" required min="0" max="100" className="form-input" value={formData.safety_score} onChange={e => setFormData({...formData, safety_score: Number(e.target.value)})} /></div>
              </div>
              <div><label className="form-label">Status</label>
                <select className="form-input" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                  <option>Available</option><option>On Trip</option><option>Off Duty</option><option>Suspended</option>
                </select>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Save Changes' : 'Add Driver'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Drivers;
