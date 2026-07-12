import React, { useState, useCallback } from 'react';
import { CheckCircle, XCircle, Info } from 'lucide-react';

// ── Global Toast Context ──────────────────────────────────────────
let _addToast = null;
export const toast = {
  success: (msg) => _addToast?.({ msg, type: 'success' }),
  error:   (msg) => _addToast?.({ msg, type: 'error' }),
  info:    (msg) => _addToast?.({ msg, type: 'info' }),
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  _addToast = useCallback((t) => {
    const id = Date.now();
    setToasts(prev => [...prev, { ...t, id }]);
    setTimeout(() => setToasts(prev => prev.filter(x => x.id !== id)), 3500);
  }, []);

  const icons = { success: <CheckCircle size={18} color="var(--success)" />, error: <XCircle size={18} color="var(--danger)" />, info: <Info size={18} color="var(--info)" /> };

  return (
    <>
      {children}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            {icons[t.type]}
            <span>{t.msg}</span>
          </div>
        ))}
      </div>
    </>
  );
};

// ── Sort helpers ──────────────────────────────────────────────────
export const useSortableData = (data, defaultKey = null, defaultDir = 'asc') => {
  const [sortKey, setSortKey] = useState(defaultKey);
  const [sortDir, setSortDir] = useState(defaultDir);

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortKey(key); setSortDir('asc'); }
  };

  const sorted = [...data].sort((a, b) => {
    if (!sortKey) return 0;
    const av = a[sortKey] ?? ''; const bv = b[sortKey] ?? '';
    if (av < bv) return sortDir === 'asc' ? -1 : 1;
    if (av > bv) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  const SortIcon = ({ k }) => {
    if (sortKey !== k) return <span style={{ opacity: 0.3, marginLeft: '4px' }}>↕</span>;
    return <span style={{ marginLeft: '4px' }}>{sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

  return { sorted, handleSort, SortIcon };
};

// ── Status Badge ──────────────────────────────────────────────────
export const StatusBadge = ({ status }) => {
  const map = {
    Available: 'badge-success', On_Trip: 'badge-info', 'On Trip': 'badge-info',
    Retired: 'badge-neutral', 'In Shop': 'badge-danger',
    Dispatched: 'badge-info', Completed: 'badge-success',
    Cancelled: 'badge-danger', Draft: 'badge-warning',
    Active: 'badge-info', Suspended: 'badge-danger', 'Off Duty': 'badge-neutral',
  };
  return <span className={`badge ${map[status] || 'badge-neutral'}`}>{status}</span>;
};

// ── Confirm Dialog ────────────────────────────────────────────────
export const useConfirm = () => {
  const [state, setState] = useState(null);
  const confirm = (msg) => new Promise(resolve => setState({ msg, resolve }));
  const Dialog = () => state ? (
    <div className="modal-backdrop" onClick={() => { state.resolve(false); setState(null); }}>
      <div className="modal-box" style={{ maxWidth: 360 }} onClick={e => e.stopPropagation()}>
        <div className="modal-title">Confirm Action</div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{state.msg}</p>
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={() => { state.resolve(false); setState(null); }}>Cancel</button>
          <button className="btn btn-danger" onClick={() => { state.resolve(true); setState(null); }}>Confirm</button>
        </div>
      </div>
    </div>
  ) : null;
  return { confirm, Dialog };
};
