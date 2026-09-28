import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Plus } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { healthMetricsAPI } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import Modal from '../../components/ui/Modal';
import toast from 'react-hot-toast';

const COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4'];

const COMMON_METRICS = [
  { name: 'Fasting Blood Sugar', unit: 'mg/dL', normal_low: 70, normal_high: 100 },
  { name: 'Hemoglobin', unit: 'g/dL', normal_low: 12, normal_high: 17 },
  { name: 'HbA1c', unit: '%', normal_low: 0, normal_high: 5.7 },
  { name: 'Total Cholesterol', unit: 'mg/dL', normal_low: 0, normal_high: 200 },
  { name: 'LDL Cholesterol', unit: 'mg/dL', normal_low: 0, normal_high: 100 },
  { name: 'HDL Cholesterol', unit: 'mg/dL', normal_low: 40, normal_high: 999 },
  { name: 'Blood Pressure Systolic', unit: 'mmHg', normal_low: 90, normal_high: 120 },
  { name: 'Serum Creatinine', unit: 'mg/dL', normal_low: 0.6, normal_high: 1.2 },
];

function TrendCard({ trend, color }) {
  const Icon = trend.trend === 'increasing' ? TrendingUp : trend.trend === 'decreasing' ? TrendingDown : Minus;
  const iconColor = trend.trend === 'increasing' ? 'text-red-500' : trend.trend === 'decreasing' ? 'text-blue-500' : 'text-gray-500';
  const data = trend.data.map(d => ({ date: new Date(d.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }), value: d.value }));

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200">{trend.name}</h3>
          <p className="text-sm text-gray-500">{trend.unit}</p>
        </div>
        <div className="flex items-center gap-2">
          {trend.latest_value != null && (
            <span className="text-xl font-bold text-gray-900 dark:text-white">{trend.latest_value}</span>
          )}
          <Icon className={`w-5 h-5 ${iconColor}`} />
        </div>
      </div>
      {trend.previous_value != null && (
        <p className="text-xs text-gray-400 mb-3">
          Previous: {trend.previous_value} {trend.unit}
          {' '} · Change: {(trend.latest_value - trend.previous_value).toFixed(1)} {trend.unit}
        </p>
      )}
      {data.length > 1 && (
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip contentStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default function HealthTrendsPage() {
  const [trends, setTrends]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm]       = useState({ metric_name: '', value: '', unit: '', recorded_date: new Date().toISOString().split('T')[0], notes: '' });
  const [saving, setSaving]   = useState(false);

  const load = () => {
    healthMetricsAPI.getTrends({ days: 180 })
      .then(r => setTrends(r.data.trends || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleAdd = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await healthMetricsAPI.add({ ...form, value: parseFloat(form.value), recorded_date: new Date(form.recorded_date).toISOString() });
      toast.success('Metric added!');
      setShowAdd(false);
      load();
    } catch { toast.error('Failed to add metric'); }
    finally { setSaving(false); }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-5xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Health Trends</h1>
          <p className="text-sm text-gray-500 mt-1">Track your health values over time</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary">
          <Plus className="w-4 h-4" /> Add Reading
        </button>
      </div>

      {trends.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No health data yet</p>
          <p className="text-sm mt-1">Upload a report or add manual readings to see trends</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {trends.map((t, i) => <TrendCard key={t.name} trend={t} color={COLORS[i % COLORS.length]} />)}
        </div>
      )}

      <DisclaimerBox text="Health trends shown are for informational purposes only. Do not make medical decisions based on these charts without consulting your doctor." />

      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Add Health Reading">
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="label">Metric Name *</label>
            <select className="input" value={form.metric_name} onChange={set('metric_name')} required>
              <option value="">Select or type below</option>
              {COMMON_METRICS.map(m => <option key={m.name} value={m.name}>{m.name} ({m.unit})</option>)}
            </select>
          </div>
          {!form.metric_name && (
            <div><label className="label">Custom Metric Name</label><input className="input" value={form.metric_name} onChange={set('metric_name')} placeholder="e.g. Weight" /></div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Value *</label><input type="number" step="0.01" className="input" value={form.value} onChange={set('value')} required /></div>
            <div>
              <label className="label">Unit *</label>
              <input className="input" value={form.unit} onChange={set('unit')} placeholder="mg/dL, kg, %" required />
            </div>
          </div>
          <div><label className="label">Date *</label><input type="date" className="input" value={form.recorded_date} onChange={set('recorded_date')} required /></div>
          <div><label className="label">Notes</label><input className="input" value={form.notes} onChange={set('notes')} placeholder="Optional notes" /></div>
          <div className="flex gap-3">
            <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
              {saving ? <span className="spinner" /> : 'Save Reading'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
