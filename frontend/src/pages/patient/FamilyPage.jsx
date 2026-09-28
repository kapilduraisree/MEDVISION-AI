import React, { useEffect, useState } from 'react';
import { Users, Plus, Edit2, Trash2, User } from 'lucide-react';
import { familyAPI } from '../../services/api';
import Modal from '../../components/ui/Modal';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

const RELATIONSHIPS = ['Spouse', 'Child', 'Parent', 'Sibling', 'Grandparent', 'Other'];
const BLOOD_GROUPS  = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export default function FamilyPage() {
  const [members, setMembers]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing]   = useState(null);
  const [saving, setSaving]     = useState(false);
  const [form, setForm]         = useState({ name: '', relationship: 'Spouse', date_of_birth: '', gender: '', blood_group: '', known_allergies: '', chronic_conditions: '', current_medications: '' });

  const load = () => {
    familyAPI.list().then(r => setMembers(r.data.members || [])).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const openAdd = () => {
    setEditing(null);
    setForm({ name: '', relationship: 'Spouse', date_of_birth: '', gender: '', blood_group: '', known_allergies: '', chronic_conditions: '', current_medications: '' });
    setShowModal(true);
  };

  const openEdit = (m) => {
    setEditing(m.id);
    setForm({ name: m.name, relationship: m.relationship || '', date_of_birth: m.date_of_birth || '', gender: m.gender || '', blood_group: m.blood_group || '', known_allergies: m.known_allergies || '', chronic_conditions: m.chronic_conditions || '', current_medications: '' });
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editing) { await familyAPI.update(editing, form); toast.success('Updated'); }
      else { await familyAPI.add(form); toast.success('Family member added'); }
      setShowModal(false); load();
    } catch { toast.error('Failed to save'); }
    finally { setSaving(false); }
  };

  const handleRemove = async (id) => {
    if (!window.confirm('Remove this family member?')) return;
    try { await familyAPI.remove(id); toast.success('Removed'); load(); }
    catch { toast.error('Failed'); }
  };

  return (
    <div className="max-w-4xl space-y-5 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Family Profiles</h1>
          <p className="text-sm text-gray-500 mt-1">Manage health profiles for your family members</p>
        </div>
        <button onClick={openAdd} className="btn-primary"><Plus className="w-4 h-4" /> Add Family Member</button>
      </div>

      {loading ? <LoadingSpinner /> : members.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <Users className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No family members added</p>
          <p className="text-sm mt-1">Add family members to manage their health records separately</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {members.map(m => (
            <div key={m.id} className="card hover:shadow-md transition-shadow group">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center text-xl font-bold text-primary-600">
                    {m.name[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">{m.name}</p>
                    <p className="text-xs text-gray-500">{m.relationship}</p>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => openEdit(m)} className="p-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 text-blue-500"><Edit2 className="w-3.5 h-3.5" /></button>
                  <button onClick={() => handleRemove(m.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 space-y-1 text-xs text-gray-500">
                {m.gender && <span className="mr-3">Gender: {m.gender}</span>}
                {m.blood_group && <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded font-medium">{m.blood_group}</span>}
                {m.date_of_birth && <p>DOB: {m.date_of_birth}</p>}
                {m.known_allergies && <p className="text-amber-600">⚠️ Allergies: {m.known_allergies}</p>}
                {m.chronic_conditions && <p>Conditions: {m.chronic_conditions}</p>}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editing ? 'Edit Family Member' : 'Add Family Member'}>
        <form onSubmit={handleSave} className="space-y-4">
          <div><label className="label">Name *</label><input className="input" value={form.name} onChange={set('name')} required /></div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Relationship</label>
              <select className="input" value={form.relationship} onChange={set('relationship')}>
                {RELATIONSHIPS.map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Gender</label>
              <select className="input" value={form.gender} onChange={set('gender')}>
                <option value="">Select</option><option>Male</option><option>Female</option><option>Other</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Date of Birth</label><input type="date" className="input" value={form.date_of_birth} onChange={set('date_of_birth')} /></div>
            <div>
              <label className="label">Blood Group</label>
              <select className="input" value={form.blood_group} onChange={set('blood_group')}>
                <option value="">Select</option>{BLOOD_GROUPS.map(b => <option key={b}>{b}</option>)}
              </select>
            </div>
          </div>
          {[{ label: 'Known Allergies', key: 'known_allergies' }, { label: 'Chronic Conditions', key: 'chronic_conditions' }, { label: 'Current Medications', key: 'current_medications' }].map(f => (
            <div key={f.key}><label className="label">{f.label}</label><textarea rows={2} className="input resize-none" value={form[f.key]} onChange={set(f.key)} /></div>
          ))}
          <div className="flex gap-3">
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
              {saving ? <span className="spinner" /> : (editing ? 'Update' : 'Add Member')}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
