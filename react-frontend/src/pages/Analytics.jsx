import React, { useState, useEffect } from 'react';
import { Download, TrendingUp, DollarSign, Activity, Zap, BarChart2 } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import api from '../api/client';
import { toast } from '../utils/ui';

const MetricCard = ({ icon, label, value, sub, color }) => (
  <div className="kpi-card" style={{ borderTop: `3px solid ${color}` }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div className="kpi-label">{label}</div>
      <div style={{ color, opacity: 0.75 }}>{icon}</div>
    </div>
    <div className="kpi-value" style={{ fontSize: '1.75rem', color }}>{value}</div>
    {sub && <div className="kpi-sub">{sub}</div>}
  </div>
);

const customTooltipStyle = {
  backgroundColor: 'var(--bg-surface)',
  border: '1px solid var(--border-color)',
  borderRadius: '8px',
  fontSize: '0.85rem',
  color: 'var(--text-primary)',
};

const Analytics = () => {
  const [kpis, setKpis] = useState(null);
  const [trips, setTrips] = useState([]);

  useEffect(() => {
    Promise.all([api.get('/analytics/kpis'), api.get('/trips/')])
      .then(([kpiRes, tripRes]) => { setKpis(kpiRes.data); setTrips(tripRes.data); })
      .catch(() => toast.error('Failed to load analytics'));
  }, []);

  const handleExportCSV = () => {
    if (!kpis) return;
    const rows = [
      ['Metric', 'Value'],
      ['Total Revenue (₹)', kpis.total_revenue],
      ['Operational Cost (₹)', kpis.operational_cost],
      ['Net Profit (₹)', kpis.total_revenue - kpis.operational_cost],
      ['ROI (%)', kpis.roi_percent],
      ['Fleet Utilization (%)', kpis.utilization_percent?.toFixed(1)],
      ['Fuel Efficiency (km/L)', kpis.fuel_efficiency_km_l],
      ['Active Vehicles', kpis.active_vehicles],
      ['Available Vehicles', kpis.available_vehicles],
      ['In Shop', kpis.in_shop_vehicles],
      ['Active Trips', kpis.active_trips],
      ['Pending Trips', kpis.pending_trips],
      ['Drivers On Duty', kpis.drivers_on_duty],
    ];
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = 'transitops_report.csv';
    a.click(); URL.revokeObjectURL(url);
    toast.success('Report exported!');
  };

  if (!kpis) return <div style={{ padding: '2rem', color: 'var(--text-muted)', textAlign: 'center' }}>Loading analytics…</div>;

  const netProfit = kpis.total_revenue - kpis.operational_cost;

  const financialData = [
    { name: 'Revenue', value: kpis.total_revenue, color: '#10b981' },
    { name: 'Op. Cost', value: kpis.operational_cost, color: '#f59e0b' },
    { name: 'Net Profit', value: netProfit, color: netProfit >= 0 ? '#3b82f6' : '#ef4444' },
  ];

  const pieData = [
    { name: 'Available', value: kpis.available_vehicles || 0, color: '#10b981' },
    { name: 'On Trip',   value: kpis.active_vehicles    || 0, color: '#3b82f6' },
    { name: 'In Shop',   value: kpis.in_shop_vehicles   || 0, color: '#ef4444' },
  ].filter(d => d.value > 0);

  // Trip status breakdown
  const tripStatus = ['Draft', 'Dispatched', 'Completed', 'Cancelled'].map(s => ({
    name: s, count: trips.filter(t => t.status === s).length,
    color: s === 'Completed' ? '#10b981' : s === 'Dispatched' ? '#3b82f6' : s === 'Cancelled' ? '#ef4444' : '#f59e0b'
  }));

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', paddingBottom: '2rem' }}>
      <div className="page-header">
        <h1 className="page-title"><TrendingUp size={22} /> Reports & Analytics</h1>
        <button className="btn btn-primary" onClick={handleExportCSV}><Download size={15} /> Export CSV</button>
      </div>

      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
        <MetricCard icon={<DollarSign size={18} />} label="Total Revenue"      value={`₹${(kpis.total_revenue||0).toLocaleString()}`}       color="var(--success)" />
        <MetricCard icon={<Activity size={18} />}   label="Operational Cost"   value={`₹${(kpis.operational_cost||0).toLocaleString()}`}     color="var(--warning)" sub="Fuel + Expenses" />
        <MetricCard icon={<TrendingUp size={18} />} label="ROI"                value={`${kpis.roi_percent||0}%`}                             color={kpis.roi_percent >= 0 ? 'var(--success)' : 'var(--danger)'} />
        <MetricCard icon={<Zap size={18} />}        label="Avg Fuel Efficiency" value={`${kpis.fuel_efficiency_km_l||0} km/L`}               color="var(--info)" sub="across all vehicles" />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>

        {/* Financial Bar Chart */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1.5rem', fontSize: '0.9375rem', fontWeight: 600 }}>Financial Overview</h3>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={financialData} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                <RechartsTooltip contentStyle={customTooltipStyle} formatter={(v) => [`₹${v.toLocaleString()}`, '']} />
                <Bar dataKey="value" radius={[5, 5, 0, 0]} maxBarSize={60} label={{ position: 'top', fill: 'var(--text-muted)', fontSize: 11, formatter: v => `₹${(v/1000).toFixed(1)}k` }}>
                  {financialData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fleet Pie Chart */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1.5rem', fontSize: '0.9375rem', fontWeight: 600 }}>Fleet Distribution</h3>
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} dataKey="value" label={({ name, value }) => `${name} (${value})`} labelLine={false}>
                  {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <RechartsTooltip contentStyle={customTooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="divider" style={{ margin: '1rem 0' }} />
          <div style={{ display: 'flex', justifyContent: 'space-around' }}>
            {pieData.map(d => (
              <div key={d.name} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.125rem', fontWeight: 700, color: d.color }}>{d.value}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{d.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trip Breakdown */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1.5rem', fontSize: '0.9375rem', fontWeight: 600 }}>Trip Status Breakdown</h3>
        <div style={{ height: 200 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={tripStatus} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
              <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
              <RechartsTooltip contentStyle={customTooltipStyle} />
              <Bar dataKey="count" radius={[5, 5, 0, 0]} maxBarSize={50} label={{ position: 'top', fill: 'var(--text-primary)', fontSize: 12, fontWeight: 600 }}>
                {tripStatus.map((d, i) => <Cell key={i} fill={d.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Net Profit Banner */}
      <div style={{ padding: '1.5rem', background: 'var(--bg-surface)', border: `1px solid ${netProfit >= 0 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`, borderLeft: `4px solid ${netProfit >= 0 ? 'var(--success)' : 'var(--danger)'}`, borderRadius: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Net Profit / Loss</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Revenue − Operational Cost</div>
        </div>
        <div style={{ fontSize: '2.25rem', fontWeight: 800, letterSpacing: '-0.04em', color: netProfit >= 0 ? 'var(--success)' : 'var(--danger)' }}>
          {netProfit >= 0 ? '+' : ''}₹{netProfit.toLocaleString()}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
