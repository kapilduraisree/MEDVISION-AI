import React, { useEffect, useState } from 'react';
import { Bell, Plus, Trash2, CheckCircle, X, Clock } from 'lucide-react';
import { remindersAPI } from '../../services/api';
import Modal from '../../components/ui/Modal';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import toast from 'react-hot-toast';

const FREQUENCIES = [
  { val: 'once_daily',       label: 'Once Daily' },
  { val: 'twice_daily',      label: 'Twice Daily' },
  { val: 'three_times_daily',label: 'Three Times Daily' },
  { val: 'four_times_daily', label: 'Four Times Daily' },
  { val: 'weekly',           label: 'Weekly' },
  { val: 'as_needed',        label: 'As Needed' },
];

function AdherenceBar({ percentage }) {
  const color = percentage >= 80 ? 'bg-green-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded-full">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${percentage}%` }} />
      </div>
      <span className="text-xs font-medium text-gray-600 dark:text-gray-400 w-10">{percentage}%</span>
    </div>
  );
}

export default function RemindersPage() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [showAdd, setShowAdd]     = useState(false);
  const [saving, setSaving]       = useState(false);
  const [form, setForm]           = useState({
    medicine_name: '', strength: '', frequency: 'once_daily',
    times: ['08:00'], start_date: '', end_date: '', instructions: '', before_after_food: 'after food',
  });

  const load = () => {
    remindersAPI.list().then(r => setSchedules(r.data.schedules || [])).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const addTime = () => setForm(f => ({ ...f, times: [...f.times, '08:00'] }));
  const setTime = (i, v) => setForm(f => ({ ...f, times: f.times.map((t, idx) => idx === i ? v : t) }));
  const removeTime = (i) => setForm(f => ({ ...f, times: f.times.filter((_, idx) => idx !== i) }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.medicine_name || !form.start_date) { toast.error('Fill required fields'); return; }
    setSaving(true);
    try {
      await remindersAPI.create(form);
      toast.success('Reminder created!');
      setShowAdd(false);
      setForm({ medicine_name: '', strength: '', frequency: 'once_daily', times: ['08:00'], start_date: '', end_date: '', instructions: '', before_after_food: 'after food' });
      load();
    } catch { toast.error('Failed to create reminder'); }
    finally { setSaving(false); }
  };

  const deactivate = async (id) => {
    if (!window.confirm('Remove this reminder?')) return;
    try { await remindersAPI.deactivate(id); toast.success('Reminder removed'); load(); }
    catch { toast.error('Failed'); }
  };

  const logDose = async (id, status) => {
    try { await remindersAPI.log(id, { status }); toast.success(`Marked as ${status}`); }
    catch { toast.error('Failed to log'); }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Medicine Reminders</h1>
          <p className="text-sm text-gray-500 mt-1">Track your medication schedule</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary">
          <Plus className="w-4 h-4" /> Add Reminder
        </button>
      </div>

      {loading ? <LoadingSpinner /> : schedules.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <Bell className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No active reminders</p>
          <p className="text-sm mt-1">Add a medicine schedule to get started</p>
          <button onClick={() => setShowAdd(true)} className="btn-primary mt-4">
            <Plus className="w-4 h-4" /> Add Your First Reminder
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {schedules.map(s => (
            <div key={s.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                    <Bell className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">{s.medicine_name}</p>
                    {s.strength && <p className="text-xs text-gray-500">{s.strength}</p>}
                  </div>
                </div>
                <button onClick={() => deactivate(s.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-1.5 text-sm text-gray-600 dark:text-gray-400 mb-3">
                <div className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-gray-400" />
                  <span className="capitalize">{s.frequency?.replace(/_/g, ' ')}</span>
                </div>
                {s.times?.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {s.times.map(t => <span key={t} className="px-2 py-0.5 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded text-xs font-medium">{t}</span>)}
                  </div>
                )}
                {s.before_after_food && <span className="text-xs text-gray-500 capitalize">{s.before_after_food}</span>}
                {s.instructions && <p className="text-xs text-gray-500 italic">{s.instructions}</p>}
                <div className="text-xs">
                  {s.start_date} {s.end_date ? `→ ${s.end_date}` : '→ Ongoing'}
                </div>
              </div>

              <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                <button onClick={() => logDose(s.id, 'taken')} className="flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium bg-green-50 text-green-700 rounded-lg hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400">
                  <CheckCircle className="w-3.5 h-3.5" /> Taken
                </button>
                <button onClick={() => logDose(s.id, 'skipped')} className="flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-400">
                  <X className="w-3.5 h-3.5" /> Skipped
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <DisclaimerBox text="Never modify your prescribed medication schedule without consulting your doctor." />

      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Add Medicine Reminder">
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="label">Medicine Name *</label>
            <input className="input" placeholder="e.g. Metformin 500mg" value={form.medicine_name} onChange={set('medicine_name')} required />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Strength</label><input className="input" placeholder="500mg" value={form.strength} onChange={set('strength')} /></div>
            <div>
              <label className="label">Food Instruction</label>
              <select className="input" value={form.before_after_food} onChange={set('before_after_food')}>
                <option>before food</option><option>after food</option><option>with food</option><option>any time</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Frequency</label>
            <select className="input" value={form.frequency} onChange={set('frequency')}>
              {FREQUENCIES.map(f => <option key={f.val} value={f.val}>{f.label}</option>)}
            </select>
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="label mb-0">Times</label>
              <button type="button" onClick={addTime} className="text-xs text-primary-600 hover:underline">+ Add time</button>
            </div>
            <div className="space-y-2">
              {form.times.map((t, i) => (
                <div key={i} className="flex gap-2">
                  <input type="time" className="input flex-1" value={t} onChange={e => setTime(i, e.target.value)} />
                  {form.times.length > 1 && (
                    <button type="button" onClick={() => removeTime(i)} className="p-2 text-gray-400 hover:text-red-500"><X className="w-4 h-4" /></button>
                  )}
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Start Date *</label><input type="date" className="input" value={form.start_date} onChange={set('start_date')} required /></div>
            <div><label className="label">End Date</label><input type="date" className="input" value={form.end_date} onChange={set('end_date')} /></div>
          </div>
          <div>
            <label className="label">Special Instructions</label>
            <input className="input" placeholder="e.g. Take with water" value={form.instructions} onChange={set('instructions')} />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
              {saving ? <span className="spinner" /> : <Bell className="w-4 h-4" />}
              {saving ? 'Saving...' : 'Create Reminder'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
