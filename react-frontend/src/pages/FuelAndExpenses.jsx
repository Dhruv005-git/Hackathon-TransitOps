import React, { useState, useEffect } from 'react';
import { Droplet, Plus, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { toast, useSortableData } from '../utils/ui';

const FuelAndExpenses = () => {
  const { user } = useAuth();
  const editable = ['Admin', 'Financial Analyst'].includes(user?.role_name);

  const [fuelLogs, setFuelLogs]   = useState([]);
  const [expenses, setExpenses]   = useState([]);
  const [vehicles, setVehicles]   = useState([]);
  const [trips, setTrips]         = useState([]);
  const [loading, setLoading]     = useState(true);
  const [isFuelModalOpen, setIsFuelModalOpen]       = useState(false);
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [fuelVehicleFilter, setFuelVehicleFilter]   = useState('All');
  const [expVehicleFilter, setExpVehicleFilter]     = useState('All');
  const [expCategoryFilter, setExpCategoryFilter]   = useState('All');
  const today = new Date().toISOString().split('T')[0];
  const [fuelForm, setFuelForm]   = useState({ vehicle_id: '', date: today, liters: '', cost: '' });
  const [expenseForm, setExpenseForm] = useState({ vehicle_id: '', trip_id: '', category: 'Toll', amount: '', date: today });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resFuel, resExp, resVehicles, resTrips] = await Promise.all([
        api.get('/fuel-logs/').catch(() => ({ data: [] })),
        api.get('/expenses/').catch(()  => ({ data: [] })),
        api.get('/vehicles/'),
        api.get('/trips/')
      ]);
      setFuelLogs(resFuel.data); setExpenses(resExp.data);
      setVehicles(resVehicles.data); setTrips(resTrips.data);
    } catch { toast.error('Failed to load data'); }
    finally { setLoading(false); }
  };
  useEffect(() => { fetchData(); }, []);

  const getVehicleReg = (vid) => vehicles.find(v => v.id === vid)?.registration_no || '—';
  const getTripCode   = (tid) => trips.find(t => t.id === tid)?.trip_code || '—';

  // Filtered fuel logs
  const filteredFuel = fuelLogs.filter(l => fuelVehicleFilter === 'All' || l.vehicle_id === Number(fuelVehicleFilter));
  const { sorted: sortedFuel, handleSort: sortFuel, SortIcon: SortFuelIcon } = useSortableData(filteredFuel, 'date', 'desc');

  // Filtered expenses
  const filteredExp = expenses.filter(e => {
    const matchV = expVehicleFilter === 'All' || e.vehicle_id === Number(expVehicleFilter);
    const matchC = expCategoryFilter === 'All' || e.category === expCategoryFilter;
    return matchV && matchC;
  });
  const { sorted: sortedExp, handleSort: sortExp, SortIcon: SortExpIcon } = useSortableData(filteredExp, 'date', 'desc');

  const totalFuelCost    = filteredFuel.reduce((s, l) => s + l.cost, 0);
  const totalExpenses    = filteredExp.reduce((s, e) => s + e.amount, 0);
  const totalOperational = totalFuelCost + totalExpenses;

  const handleFuelSubmit = async (e) => {
    e.preventDefault();
    try { await api.post('/fuel-logs/', fuelForm); toast.success('Fuel log saved'); setIsFuelModalOpen(false); fetchData(); }
    catch (err) { toast.error(err.response?.data?.detail || 'Error logging fuel'); }
  };

  const handleExpenseSubmit = async (e) => {
    e.preventDefault();
    try { await api.post('/expenses/', expenseForm); toast.success('Expense saved'); setIsExpenseModalOpen(false); fetchData(); }
    catch (err) { toast.error(err.response?.data?.detail || 'Error adding expense'); }
  };

  return (
    <div className="animate-fade-in">

      <div className="page-header">
        <h1 className="page-title"><Droplet size={22} /> Fuel & Expense Management</h1>
        {editable && (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-primary" onClick={() => setIsFuelModalOpen(true)}><Plus size={15} /> Log Fuel</button>
            <button className="btn btn-accent"  onClick={() => setIsExpenseModalOpen(true)}><Plus size={15} /> Add Expense</button>
          </div>
        )}
      </div>

      {/* Summary KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="kpi-card" style={{ borderTop: '3px solid var(--info)' }}>
          <div className="kpi-label">Fuel Cost (filtered)</div>
          <div className="kpi-value" style={{ fontSize: '1.5rem', color: 'var(--info)' }}>₹{totalFuelCost.toLocaleString()}</div>
        </div>
        <div className="kpi-card" style={{ borderTop: '3px solid var(--warning)' }}>
          <div className="kpi-label">Other Expenses (filtered)</div>
          <div className="kpi-value" style={{ fontSize: '1.5rem', color: 'var(--warning)' }}>₹{totalExpenses.toLocaleString()}</div>
        </div>
        <div className="kpi-card" style={{ borderTop: '3px solid var(--accent)' }}>
          <div className="kpi-label">Total Operational Cost</div>
          <div className="kpi-value" style={{ fontSize: '1.5rem', color: 'var(--accent)' }}>₹{totalOperational.toLocaleString()}</div>
        </div>
      </div>

      {/* Fuel Logs Section */}
      <div className="section-label" style={{ marginTop: '0.5rem' }}>Fuel Logs</div>
      <div className="filter-bar" style={{ marginBottom: '0.75rem' }}>
        <select className="form-input" style={{ width: 200 }} value={fuelVehicleFilter} onChange={e => setFuelVehicleFilter(e.target.value)}>
          <option value="All">All Vehicles</option>
          {vehicles.map(v => <option key={v.id} value={v.id}>{v.registration_no}</option>)}
        </select>
        <div style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{sortedFuel.length} records</div>
      </div>
      <div className="table-wrapper" style={{ marginBottom: '2rem' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Trip</th>
              <th className="sortable" onClick={() => sortFuel('date')}>Date <SortFuelIcon k="date" /></th>
              <th className="sortable" onClick={() => sortFuel('liters')}>Liters <SortFuelIcon k="liters" /></th>
              <th className="sortable" onClick={() => sortFuel('cost')}>Cost (₹) <SortFuelIcon k="cost" /></th>
              <th>Cost/Liter</th>
            </tr>
          </thead>
          <tbody>
            {loading ? <tr className="loading-row"><td colSpan="6">Loading…</td></tr>
            : sortedFuel.length === 0 ? <tr><td colSpan="6"><div className="empty-state"><Droplet size={32} /><p>No fuel logs found.</p></div></td></tr>
            : sortedFuel.map(log => (
              <tr key={log.id}>
                <td style={{ fontFamily: 'monospace', fontWeight: 600, fontSize: '0.85rem' }}>{getVehicleReg(log.vehicle_id)}</td>
                <td><span className="badge badge-neutral">{getTripCode(log.trip_id)}</span></td>
                <td>{log.date}</td>
                <td>{log.liters.toLocaleString()} L</td>
                <td style={{ fontWeight: 600 }}>₹{log.cost.toLocaleString()}</td>
                <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>₹{(log.cost / log.liters).toFixed(2)}/L</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Expenses Section */}
      <div className="section-label">Other Expenses (Toll / Misc)</div>
      <div className="filter-bar" style={{ marginBottom: '0.75rem' }}>
        <select className="form-input" style={{ width: 200 }} value={expVehicleFilter} onChange={e => setExpVehicleFilter(e.target.value)}>
          <option value="All">All Vehicles</option>
          {vehicles.map(v => <option key={v.id} value={v.id}>{v.registration_no}</option>)}
        </select>
        <select className="form-input" style={{ width: 180 }} value={expCategoryFilter} onChange={e => setExpCategoryFilter(e.target.value)}>
          <option value="All">All Categories</option>
          <option>Toll</option><option>Fines</option><option>Driver Allowance</option><option>Miscellaneous</option>
        </select>
        <div style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{sortedExp.length} records</div>
      </div>
      <div className="table-wrapper" style={{ marginBottom: '1.5rem' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Trip</th>
              <th>Vehicle</th>
              <th>Category</th>
              <th className="sortable" onClick={() => sortExp('date')}>Date <SortExpIcon k="date" /></th>
              <th className="sortable" onClick={() => sortExp('amount')}>Amount (₹) <SortExpIcon k="amount" /></th>
            </tr>
          </thead>
          <tbody>
            {loading ? <tr className="loading-row"><td colSpan="5">Loading…</td></tr>
            : sortedExp.length === 0 ? <tr><td colSpan="5"><div className="empty-state"><TrendingUp size={32} /><p>No expenses found.</p></div></td></tr>
            : sortedExp.map(exp => (
              <tr key={exp.id}>
                <td><span className="badge badge-neutral">{getTripCode(exp.trip_id)}</span></td>
                <td style={{ fontFamily: 'monospace', fontWeight: 600, fontSize: '0.85rem' }}>{getVehicleReg(exp.vehicle_id)}</td>
                <td><span className={`badge ${exp.category === 'Toll' ? 'badge-info' : exp.category === 'Fines' ? 'badge-danger' : 'badge-neutral'}`}>{exp.category}</span></td>
                <td>{exp.date}</td>
                <td style={{ fontWeight: 600 }}>₹{exp.amount.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.25rem 1.5rem', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '10px', borderLeft: '4px solid var(--accent)' }}>
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.25rem' }}>Total Operational Cost (Fuel + Misc)</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Fuel: ₹{totalFuelCost.toLocaleString()} + Expenses: ₹{totalExpenses.toLocaleString()}</div>
        </div>
        <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent)', letterSpacing: '-0.04em' }}>₹{totalOperational.toLocaleString()}</div>
      </div>

      {/* Fuel Modal */}
      {isFuelModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsFuelModalOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Log Fuel</div>
            <form onSubmit={handleFuelSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div><label className="form-label">Vehicle</label>
                <select required className="form-input" value={fuelForm.vehicle_id} onChange={e => setFuelForm({...fuelForm, vehicle_id: Number(e.target.value)})}>
                  <option value="">Select vehicle…</option>
                  {vehicles.map(v => <option key={v.id} value={v.id}>{v.registration_no}</option>)}
                </select>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">Liters</label><input type="number" step="0.1" required className="form-input" value={fuelForm.liters} onChange={e => setFuelForm({...fuelForm, liters: Number(e.target.value)})} /></div>
                <div style={{ flex: 1 }}><label className="form-label">Total Cost (₹)</label><input type="number" required className="form-input" value={fuelForm.cost} onChange={e => setFuelForm({...fuelForm, cost: Number(e.target.value)})} /></div>
              </div>
              <div><label className="form-label">Date</label><input type="date" required className="form-input" value={fuelForm.date} onChange={e => setFuelForm({...fuelForm, date: e.target.value})} /></div>
              {fuelForm.liters > 0 && fuelForm.cost > 0 && (
                <div style={{ padding: '0.75rem', background: 'rgba(59,130,246,0.08)', borderRadius: '7px', fontSize: '0.85rem', color: 'var(--info)' }}>
                  Cost per Liter: <strong>₹{(fuelForm.cost / fuelForm.liters).toFixed(2)}</strong>
                </div>
              )}
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setIsFuelModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Log</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Expense Modal */}
      {isExpenseModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsExpenseModalOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Add Expense</div>
            <form onSubmit={handleExpenseSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div><label className="form-label">Vehicle</label>
                <select required className="form-input" value={expenseForm.vehicle_id} onChange={e => setExpenseForm({...expenseForm, vehicle_id: Number(e.target.value)})}>
                  <option value="">Select vehicle…</option>
                  {vehicles.map(v => <option key={v.id} value={v.id}>{v.registration_no}</option>)}
                </select>
              </div>
              <div><label className="form-label">Trip (Optional)</label>
                <select className="form-input" value={expenseForm.trip_id} onChange={e => setExpenseForm({...expenseForm, trip_id: e.target.value ? Number(e.target.value) : ''})}>
                  <option value="">None</option>
                  {trips.map(t => <option key={t.id} value={t.id}>{t.trip_code} — {t.source} → {t.destination}</option>)}
                </select>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><label className="form-label">Category</label>
                  <select className="form-input" value={expenseForm.category} onChange={e => setExpenseForm({...expenseForm, category: e.target.value})}>
                    <option>Toll</option><option>Fines</option><option>Driver Allowance</option><option>Miscellaneous</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}><label className="form-label">Amount (₹)</label><input type="number" required className="form-input" value={expenseForm.amount} onChange={e => setExpenseForm({...expenseForm, amount: Number(e.target.value)})} /></div>
              </div>
              <div><label className="form-label">Date</label><input type="date" required className="form-input" value={expenseForm.date} onChange={e => setExpenseForm({...expenseForm, date: e.target.value})} /></div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setIsExpenseModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-accent">Save Expense</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FuelAndExpenses;
