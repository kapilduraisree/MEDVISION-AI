import React, { useState } from 'react';
import { Pill, Plus, Save } from 'lucide-react';
import { adminAPI } from '../../services/api';
import Modal from '../../components/ui/Modal';
import toast from 'react-hot-toast';

export default function AdminMedicines() {
  const [showAdd, setShowAdd] = useState(false);
  const [saving, setSaving]   = useState(false);
  const [form, setForm] = useState({
    brand_name: '', generic_name: '', active_ingredient: '', drug_category: '',
    general_purpose: '', common_precautions: '', common_side_effects: '',
    storage_information: '', important_warnings: '', manufacturer: '',
    drug_class: '', is_otc: false, requires_prescription: true,
  });

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.brand_name) { toast.error('Brand name required'); return; }
    setSaving(true);
    try {
      await adminAPI.addMedicine(form);
      toast.success('Medicine added to database');
      setShowAdd(false);
      setForm({ brand_name: '', generic_name: '', active_ingredient: '', drug_category: '', general_purpose: '', common_precautions: '', common_side_effects: '', storage_information: '', important_warnings: '', manufacturer: '', drug_class: '', is_otc: false, requires_prescription: true });
    } catch { toast.error('Failed to add medicine'); }
    finally { setSaving(false); }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <div><h1 className="page-title">Medicine Database</h1><p className="text-sm text-gray-500">Manage verified medicine information</p></div>
        <button onClick={() => setShowAdd(true)} className="btn-primary"><Plus className="w-4 h-4" />Add Medicine</button>
      </div>
      <div className="card p-8 text-center text-gray-400">
        <Pill className="w-12 h-12 mx-auto mb-3 opacity-40" />
        <p className="font-medium">Medicine database is loaded from sample data</p>
        <p className="text-sm mt-1">Use the Add Medicine button to add new entries</p>
      </div>
      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Add Medicine to Database" size="lg">
        <form onSubmit={handleSave} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Brand Name *</label><input className="input" value={form.brand_name} onChange={set('brand_name')} required /></div>
            <div><label className="label">Generic Name</label><input className="input" value={form.generic_name} onChange={set('generic_name')} /></div>
            <div><label className="label">Active Ingredient</label><input className="input" value={form.active_ingredient} onChange={set('active_ingredient')} /></div>
            <div><label className="label">Drug Category</label><input className="input" value={form.drug_category} onChange={set('drug_category')} /></div>
            <div><label className="label">Drug Class</label><input className="input" value={form.drug_class} onChange={set('drug_class')} /></div>
            <div><label className="label">Manufacturer</label><input className="input" value={form.manufacturer} onChange={set('manufacturer')} /></div>
          </div>
          {[{ k: 'general_purpose', l: 'General Purpose' }, { k: 'common_precautions', l: 'Precautions' }, { k: 'common_side_effects', l: 'Side Effects' }, { k: 'storage_information', l: 'Storage' }, { k: 'important_warnings', l: 'Warnings' }].map(f => (
            <div key={f.k}><label className="label">{f.l}</label><textarea rows={2} className="input resize-none" value={form[f.k]} onChange={set(f.k)} /></div>
          ))}
          <div className="flex gap-4">
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_otc} onChange={set('is_otc')} />Over the Counter (OTC)</label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.requires_prescription} onChange={set('requires_prescription')} />Requires Prescription</label>
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
              {saving ? <span className="spinner" /> : <Save className="w-4 h-4" />} Add Medicine
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
