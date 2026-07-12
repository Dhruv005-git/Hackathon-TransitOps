import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Truck, Shield, User, TrendingUp, DollarSign } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch (err) {
      setError('Invalid credentials or server error.');
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', width: '100%', fontFamily: 'Inter, sans-serif' }}>
      {/* LEFT SIDE - Branding */}
      <div style={{
        flex: 1,
        backgroundColor: '#161921',
        color: '#ffffff',
        padding: '4rem',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '6rem' }}>
          <div style={{ 
            backgroundColor: '#ff6600', 
            padding: '0.5rem', 
            borderRadius: '6px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center' 
          }}>
            <Truck size={24} color="white" />
          </div>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.02em' }}>TransitOps</span>
        </div>

        {/* Copy */}
        <div style={{ maxWidth: '450px', zIndex: 10 }}>
          <h1 style={{ 
            fontSize: '3.5rem', 
            fontWeight: 700, 
            lineHeight: 1.1, 
            marginBottom: '1.5rem',
            letterSpacing: '-0.03em',
            color: '#ffffff'
          }}>
            Industrial-grade fleet intelligence.
          </h1>
          <p style={{ 
            fontSize: '1.25rem', 
            color: '#d4d4d8', 
            lineHeight: 1.6,
            fontWeight: 400
          }}>
            Ditch the spreadsheets. Register vehicles, dispatch trips, log maintenance, and control costs from a single command center.
          </p>
        </div>

        {/* Background Watermark */}
        <div style={{
          position: 'absolute',
          bottom: '-2rem',
          left: '2rem',
          fontSize: '12rem',
          fontWeight: 900,
          color: 'rgba(255,255,255,0.02)',
          lineHeight: 0.8,
          pointerEvents: 'none',
          userSelect: 'none',
          whiteSpace: 'nowrap'
        }}>
          T-OPS<br/>SYS_
        </div>
      </div>

      {/* RIGHT SIDE - Login Form */}
      <div style={{
        flex: 1,
        backgroundColor: '#f6f6f5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem'
      }}>
        <div style={{ width: '100%', maxWidth: '480px' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '0.25rem', color: '#111827', letterSpacing: '-0.03em' }}>System Access</h2>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem', fontSize: '1rem' }}>Sign in with a demo role account to continue.</p>

          {error && (
            <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem', color: '#111827' }}>Email</label>
              <input
                type="email"
                placeholder="role@transitops.app"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  borderRadius: '6px',
                  border: '1px solid #d1d5db',
                  fontSize: '1rem',
                  outline: 'none',
                  backgroundColor: '#ffffff'
                }}
              />
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem', color: '#111827' }}>Password</label>
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  borderRadius: '6px',
                  border: '1px solid #d1d5db',
                  fontSize: '1rem',
                  outline: 'none',
                  backgroundColor: '#ffffff'
                }}
              />
            </div>
            <button 
              type="submit" 
              style={{ 
                width: '100%', 
                padding: '0.875rem', 
                backgroundColor: '#ff6600', 
                color: 'white', 
                fontWeight: 700, 
                fontSize: '1rem', 
                border: 'none', 
                borderRadius: '6px', 
                cursor: 'pointer',
                letterSpacing: '0.05em'
              }}>
              AUTHENTICATE
            </button>
          </form>

          <div style={{ display: 'flex', alignItems: 'center', margin: '1.5rem 0' }}>
            <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }}></div>
            <span style={{ padding: '0 1rem', fontSize: '0.75rem', color: '#9ca3af', letterSpacing: '0.05em', fontFamily: 'monospace', textTransform: 'uppercase' }}>Quick Access Roles</span>
            <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }}></div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            {[
              { role: 'Admin', email: 'admin@transitops.com', icon: <Shield size={18} />, color: 'rgba(239, 68, 68, 0.1)', iconColor: '#ef4444' },
              { role: 'Fleet Manager', email: 'fleet@transitops.com', icon: <Truck size={18} />, color: 'rgba(59, 130, 246, 0.1)', iconColor: '#3b82f6' },
              { role: 'Driver', email: 'driver@transitops.com', icon: <User size={18} />, color: 'rgba(16, 185, 129, 0.1)', iconColor: '#10b981' },
              { role: 'Safety Officer', email: 'safety@transitops.com', icon: <TrendingUp size={18} />, color: 'rgba(245, 158, 11, 0.1)', iconColor: '#f59e0b' },
              { role: 'Financial Analyst', email: 'finance@transitops.com', icon: <DollarSign size={18} />, color: 'rgba(168, 85, 247, 0.1)', iconColor: '#a855f7' },
            ].map((acc, idx) => (
              <button
                key={acc.role}
                type="button"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.6rem 0.75rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  width: '100%',
                  background: '#ffffff',
                  cursor: 'pointer',
                  textAlign: 'left'
                }}
                onClick={() => {
                  setEmail(acc.email);
                  setPassword(acc.email.split('@')[0] + '123'); 
                }}
              >
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  background: acc.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '0.75rem',
                  color: acc.iconColor,
                  flexShrink: 0
                }}>
                  {acc.icon}
                </div>
                <div style={{ overflow: 'hidden' }}>
                  <div style={{ fontWeight: 600, color: '#111827', fontSize: '0.85rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{acc.role}</div>
                  <div style={{ fontSize: '0.7rem', color: '#6b7280', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{acc.email}</div>
                </div>
              </button>
            ))}
          </div>

        </div>
      </div>
    </div>
  );
};

export default Login;
