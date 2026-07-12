import React, { useState } from 'react';
import { Save } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Settings = () => {
  const { user } = useAuth();
  const editable = ['Admin'].includes(user?.role_name);
  
  const [formData, setFormData] = useState({
    depot_name: 'Gandhinagar Depot GJ4',
    currency: 'INR (Rs)',
    distance_unit: 'Kilometers'
  });

  const handleSave = (e) => {
    e.preventDefault();
    alert('Settings saved successfully!');
  };

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>⚙️ Settings & RBAC</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        
        {/* Left Form: General Settings */}
        <div className="card" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>GENERAL</h3>
          <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label className="form-label">DEPOT NAME</label>
              <input 
                type="text" className="form-input" 
                value={formData.depot_name} 
                onChange={e => setFormData({...formData, depot_name: e.target.value})}
                disabled={!editable}
              />
            </div>
            <div>
              <label className="form-label">CURRENCY</label>
              <input 
                type="text" className="form-input" 
                value={formData.currency} 
                onChange={e => setFormData({...formData, currency: e.target.value})}
                disabled={!editable}
              />
            </div>
            <div>
              <label className="form-label">DISTANCE UNIT</label>
              <input 
                type="text" className="form-input" 
                value={formData.distance_unit} 
                onChange={e => setFormData({...formData, distance_unit: e.target.value})}
                disabled={!editable}
              />
            </div>
            
            {editable && (
              <div style={{ marginTop: '1rem' }}>
                <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                  <Save size={16} /> Save Changes
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Right Table: RBAC Matrix */}
        <div className="card" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>ROLE-BASED ACCESS (RBAC)</h3>
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th style={{ fontSize: '0.75rem' }}>ROLE</th>
                  <th style={{ fontSize: '0.75rem', textAlign: 'center' }}>FLEET</th>
                  <th style={{ fontSize: '0.75rem', textAlign: 'center' }}>DRIVERS</th>
                  <th style={{ fontSize: '0.75rem', textAlign: 'center' }}>TRIPS</th>
                  <th style={{ fontSize: '0.75rem', textAlign: 'center' }}>FUEL/EXP.</th>
                  <th style={{ fontSize: '0.75rem', textAlign: 'center' }}>ANALYTICS</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: 500 }}>Admin</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 500 }}>Fleet Manager</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 500 }}>Dispatcher</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>view</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 500 }}>Safety Officer</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>view</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 500 }}>Financial Analyst</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>view</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>—</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                  <td style={{ textAlign: 'center' }}>✓</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Settings;
