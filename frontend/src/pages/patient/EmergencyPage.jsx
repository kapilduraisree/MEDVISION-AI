import React, { useEffect, useState } from 'react';
import { AlertTriangle, Phone, Plus, Trash2, Shield } from 'lucide-react';
import { emergencyAPI } from '../../services/api';
import Modal from '../../components/ui/Modal';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

export default function EmergencyPage() {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [showAdd, setShowAdd]   = useState(false);
  const [saving, setSaving]     = useState(false);
  const [form, setForm]         = useState({ name: '', relationship: '', phone: '', alternate_phone: '', email: '', is_primary: false });

  const load = () => {
    emergencyAPI.listContacts().then(r => setContacts(r.data.contacts || [])).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try { await emergencyAPI.addContact(form); toast.success('Contact added'); setShowAdd(false); load(); }
    catch { toast.error('Failed to add contact'); }
    finally { setSaving(false); }
  };

  return (
    <div className="max-w-3xl space-y-5 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Emergency</h1>
          <p className="text-sm text-gray-500 mt-1">Emergency contacts and urgent care information</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary"><Plus className="w-4 h-4" />Add Contact</button>
      </div>

      {/* Emergency numbers */}
      <div className="card border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/10">
        <h2 className="font-bold text-red-700 dark:text-red-400 mb-3 flex items-center gap-2"><AlertTriangle className="w-5 h-5" />Emergency Numbers (India)</h2>
        <div className="grid grid-cols-2 gap-3">
          {[{ label: 'Emergency', num: '112' }, { label: 'Ambulance', num: '108' }, { label: 'Police', num: '100' }, { label: 'Fire', num: '101' }].map(e => (
            <a key={e.label} href={`tel:${e.num}`} className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-red-200 dark:border-red-700 hover:bg-red-50 dark:hover:bg-red-900/20">
              <div className="w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                <Phone className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <p className="font-bold text-red-700 dark:text-red-400 text-lg">{e.num}</p>
                <p className="text-xs text-gray-500">{e.label}</p>
              </div>
            </a>
          ))}
        </div>
        <div className="mt-3 p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
          <p className="text-sm font-medium text-red-800 dark:text-red-300">
            ⚠️ In a medical emergency, call 112 immediately. This system cannot provide emergency medical assistance.
          </p>
        </div>
      </div>

      {/* Contacts */}
      <div className="card">
        <h2 className="section-title flex items-center gap-2"><Shield className="w-4 h-4" />My Emergency Contacts</h2>
        {loading ? <LoadingSpinner /> : contacts.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <Phone className="w-10 h-10 mx-auto mb-2 opacity-40" />
            <p className="text-sm">No emergency contacts added</p>
          </div>
        ) : (
          <div className="space-y-3">
            {contacts.map(c => (
              <div key={c.id} className={`flex items-center justify-between p-3 rounded-lg border ${c.is_primary ? 'border-red-200 bg-red-50 dark:bg-red-900/10' : 'border-gray-200 dark:border-gray-700'}`}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center font-bold text-gray-600 dark:text-gray-300">
                    {c.name[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                      {c.name}
                      {c.is_primary && <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">Primary</span>}
                    </p>
                    <p className="text-xs text-gray-500">{c.relationship}</p>
                    <a href={`tel:${c.phone}`} className="text-sm text-primary-600 hover:underline font-medium">{c.phone}</a>
                    {c.alternate_phone && <span className="text-xs text-gray-400 ml-2">{c.alternate_phone}</span>}
                  </div>
                </div>
                <button onClick={async () => { try { await emergencyAPI.deleteContact(c.id); load(); } catch {} }} className="p-1.5 rounded-lg hover:bg-red-50 text-red-400">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Add Emergency Contact">
        <form onSubmit={handleSave} className="space-y-4">
          <div><label className="label">Name *</label><input className="input" value={form.name} onChange={set('name')} required /></div>
          <div><label className="label">Relationship</label><input className="input" placeholder="e.g. Spouse, Parent" value={form.relationship} onChange={set('relationship')} /></div>
          <div><label className="label">Phone *</label><input type="tel" className="input" value={form.phone} onChange={set('phone')} required /></div>
          <div><label className="label">Alternate Phone</label><input type="tel" className="input" value={form.alternate_phone} onChange={set('alternate_phone')} /></div>
          <div><label className="label">Email</label><input type="email" className="input" value={form.email} onChange={set('email')} /></div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="primary" checked={form.is_primary} onChange={set('is_primary')} className="w-4 h-4 text-primary-600" />
            <label htmlFor="primary" className="text-sm text-gray-700 dark:text-gray-300">Set as primary contact</label>
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
              {saving ? <span className="spinner" /> : 'Add Contact'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
