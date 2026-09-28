import React, { useState } from 'react';
import { Settings, Lock, Globe, Moon, Sun, Save } from 'lucide-react';
import { usersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { user, updateUser } = useAuth();
  const [pwForm, setPwForm]   = useState({ current_password: '', new_password: '', confirm: '' });
  const [saving, setSaving]   = useState(false);
  const [dark, setDark]       = useState(document.documentElement.classList.contains('dark'));

  const setP = k => e => setPwForm(f => ({ ...f, [k]: e.target.value }));

  const changePw = async (e) => {
    e.preventDefault();
    if (pwForm.new_password !== pwForm.confirm) { toast.error('Passwords do not match'); return; }
    setSaving(true);
    try {
      await usersAPI.changePassword({ current_password: pwForm.current_password, new_password: pwForm.new_password });
      toast.success('Password changed successfully');
      setPwForm({ current_password: '', new_password: '', confirm: '' });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to change password');
    } finally { setSaving(false); }
  };

  const toggleDark = () => {
    const next = !dark; setDark(next);
    document.documentElement.classList.toggle('dark', next);
    updateUser({ dark_mode: next });
  };

  const changeLang = (lang) => {
    usersAPI.updateProfile({ preferred_language: lang }).then(() => {
      updateUser({ preferred_language: lang });
      toast.success('Language updated');
    }).catch(() => {});
  };

  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
      </div>

      {/* Account info */}
      <div className="card space-y-3">
        <h2 className="section-title flex items-center gap-2"><Settings className="w-4 h-4" />Account Information</h2>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div><p className="text-gray-500">Name</p><p className="font-medium text-gray-900 dark:text-white">{user?.full_name}</p></div>
          <div><p className="text-gray-500">Email</p><p className="font-medium text-gray-900 dark:text-white">{user?.email}</p></div>
          <div><p className="text-gray-500">Role</p><p className="font-medium text-gray-900 dark:text-white capitalize">{user?.role}</p></div>
          <div><p className="text-gray-500">Language</p><p className="font-medium text-gray-900 dark:text-white">{user?.preferred_language === 'ta' ? 'Tamil' : 'English'}</p></div>
        </div>
      </div>

      {/* Appearance */}
      <div className="card space-y-4">
        <h2 className="section-title flex items-center gap-2"><Sun className="w-4 h-4" />Appearance</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-sm text-gray-900 dark:text-white">Dark Mode</p>
            <p className="text-xs text-gray-500">Switch between light and dark theme</p>
          </div>
          <button onClick={toggleDark} className={`w-12 h-6 rounded-full transition-colors relative ${dark ? 'bg-primary-600' : 'bg-gray-300'}`}>
            <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${dark ? 'translate-x-7' : 'translate-x-1'}`} />
          </button>
        </div>
      </div>

      {/* Language */}
      <div className="card space-y-4">
        <h2 className="section-title flex items-center gap-2"><Globe className="w-4 h-4" />Language</h2>
        <div className="flex gap-3">
          {[{ val: 'en', label: '🇬🇧 English' }, { val: 'ta', label: '🇮🇳 தமிழ்' }].map(l => (
            <button key={l.val} onClick={() => changeLang(l.val)}
              className={`px-5 py-2.5 rounded-lg text-sm font-medium border transition-colors ${user?.preferred_language === l.val ? 'bg-primary-600 text-white border-primary-600' : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50'}`}>
              {l.label}
            </button>
          ))}
        </div>
      </div>

      {/* Change password */}
      <div className="card space-y-4">
        <h2 className="section-title flex items-center gap-2"><Lock className="w-4 h-4" />Change Password</h2>
        <form onSubmit={changePw} className="space-y-3">
          <div><label className="label">Current Password</label><input type="password" className="input" value={pwForm.current_password} onChange={setP('current_password')} required /></div>
          <div><label className="label">New Password (min 8 chars)</label><input type="password" className="input" value={pwForm.new_password} onChange={setP('new_password')} required /></div>
          <div><label className="label">Confirm New Password</label><input type="password" className="input" value={pwForm.confirm} onChange={setP('confirm')} required /></div>
          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? <span className="spinner" /> : <Save className="w-4 h-4" />}
            {saving ? 'Saving...' : 'Change Password'}
          </button>
        </form>
      </div>

      {/* Disclaimer */}
      <div className="card border-amber-200 bg-amber-50 dark:bg-amber-900/10 dark:border-amber-700 p-4">
        <p className="text-xs text-amber-800 dark:text-amber-300 font-medium">
          ⚠️ MedVision AI is designed for educational and informational purposes only. All AI-generated content must be reviewed by a qualified healthcare professional before any clinical decision.
        </p>
      </div>
    </div>
  );
}
