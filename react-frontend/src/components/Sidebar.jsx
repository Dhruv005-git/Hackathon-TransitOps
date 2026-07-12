import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  MapPin, 
  Truck, 
  Users, 
  Wrench, 
  LogOut, 
  UserCircle,
  Droplet,
  Receipt,
  BarChart2
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';

const Sidebar = () => {
  const { user, logout } = useAuth();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} />, roles: ['Admin', 'Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst', 'Driver'] },
    { label: 'Fleet', path: '/fleet', icon: <Truck size={20} />, roles: ['Admin', 'Fleet Manager', 'Dispatcher', 'Financial Analyst'] },
    { label: 'Drivers', path: '/drivers', icon: <Users size={20} />, roles: ['Admin', 'Fleet Manager', 'Safety Officer'] },
    { label: 'My Trips', path: '/trips', icon: <MapPin size={20} />, roles: ['Admin', 'Dispatcher', 'Safety Officer', 'Driver'] },
    { label: 'Maintenance', path: '/maintenance', icon: <Wrench size={20} />, roles: ['Admin', 'Fleet Manager'] },
    { label: 'Fuel & Expenses', path: '/fuel-expenses', icon: <Droplet size={20} />, roles: ['Admin', 'Financial Analyst'] },
    { label: 'Analytics', path: '/analytics', icon: <BarChart2 size={20} />, roles: ['Admin', 'Fleet Manager', 'Financial Analyst'] },
    { label: 'Settings', path: '/settings', icon: <Receipt size={20} />, roles: ['Admin'] },
  ];

  return (
    <div style={{
      width: '260px',
      flexShrink: 0,
      backgroundColor: 'var(--bg-surface)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      padding: '1.5rem',
      height: '100vh',
      position: 'sticky',
      top: 0
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem' }}>
        <div style={{ 
          backgroundColor: '#2563eb', 
          padding: '0.5rem', 
          borderRadius: '8px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}>
          <Truck size={22} color="white" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.25rem', margin: 0, fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>TransitOps</h2>
        </div>
        <div style={{ marginLeft: 'auto' }}>
          <ThemeToggle />
        </div>
      </div>

      {/* User Profile */}
      <div style={{
        padding: '1rem',
        backgroundColor: 'var(--bg-base)',
        borderRadius: '8px',
        marginBottom: '2rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        border: '1px solid var(--border-color)'
      }}>
        <UserCircle size={32} color="var(--primary)" />
        <div style={{ overflow: 'hidden' }}>
          <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user?.name}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{user?.role_name}</div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        {navItems.filter(item => item.roles.includes(user?.role_name)).map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              textDecoration: 'none',
              color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
              backgroundColor: isActive ? 'rgba(37, 99, 235, 0.08)' : 'transparent',
              fontWeight: isActive ? 600 : 500,
              transition: 'all 0.2s ease',
            })}
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
        <button
          onClick={logout}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            width: '100%',
            padding: '0.75rem 1rem',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            fontWeight: 500,
            cursor: 'pointer',
            borderRadius: '8px',
            transition: 'all 0.2s ease',
          }}
          onMouseOver={(e) => { e.currentTarget.style.color = 'var(--danger)'; e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.08)'; }}
          onMouseOut={(e) => { e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.backgroundColor = 'transparent'; }}
        >
          <LogOut size={20} />
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
