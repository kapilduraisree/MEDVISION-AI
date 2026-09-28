import React, { useEffect, useState } from 'react';
import { User, Save, Camera } from 'lucide-react';
import { patientsAPI, usersAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export default function PatientProfile() {
  const { user, updateUser } = useAuth();
  const [profile, setProfile]   = useState(null);
  const [loading, setLoading]   = useState(true);
  const [saving, setSaving]     = useState(false);
  const [userForm, setUserForm] = useState({ full_name: '', phone: '' });
  const [patForm, setPatForm]   = useState({});

  useEffect(() => {
    patientsAPI.getProfile().then(r => {
      setProfile(r.data);
      setUserForm({ full_name: r.data.user.full_name, phone: r.data.user.phone || '' });
      setPatForm(r.data.patient || {});
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await Promise.all([
        usersAPI.updateProfile(userForm),
        patientsAPI.updateProfile(patForm),
      ]);
      updateUser({ full_name: userForm.full_name, phone: userForm.phone });
      toast.success('Profile updated successfully');
    } catch {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const setPat = (k) => (e) => setPatForm(f => ({ ...f, [k]: e.target.value }));
  const setUsr = (k) => (e) => setUserForm(f => ({ ...f, [k]: e.target.value }));

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">My Profile</h1>
        <button onClick={handleSave} disabled={saving} className="btn-primary">
          {saving ? <span className="spinner" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Avatar */}
      <div className="card flex items-center gap-5">
        <div className="relative">
          <div className="w-20 h-20 rounded-full bg-primary-600 flex items-center justify-center text-white text-3xl font-bold">
            {user?.full_name?.[0] || 'P'}
          </div>
          <label className="absolute bottom-0 right-0 w-7 h-7 bg-white dark:bg-gray-700 rounded-full border-2 border-gray-200 flex items-center justify-center cursor-pointer hover:bg-gray-50">
            <Camera className="w-3.5 h-3.5 text-gray-600" />
            <input type="file" accept="image/*" className="hidden" onChange={async e => {
              const f = e.target.files[0]; if (!f) return;
              const fd = new FormData(); fd.append('file', f);
              try {
                const r = await usersAPI.uploadImage(fd);
                updateUser({ profile_image: r.data.profile_image });
                toast.success('Profile image updated');
              } catch { toast.error('Failed to upload image'); }
            }} />
          </label>
        </div>
        <div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">{user?.full_name}</p>
          <p className="text-sm text-gray-500">{user?.email}</p>
          <span className="inline-block mt-1 px-2 py-0.5 bg-primary-100 text-primary-700 text-xs rounded-full capitalize">{user?.role}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personal Info */}
        <div className="card space-y-4">
          <h2 className="section-title">Personal Information</h2>
          {[
            { label: 'Full Name',    key: 'full_name', type: 'text',  form: 'user' },
            { label: 'Phone',        key: 'phone',     type: 'tel',   form: 'user' },
          ].map(f => (
            <div key={f.key}>
              <label className="label">{f.label}</label>
              <input
                type={f.type} className="input"
                value={f.form === 'user' ? userForm[f.key] || '' : patForm[f.key] || ''}
                onChange={f.form === 'user' ? setUsr(f.key) : setPat(f.key)}
              />
            </div>
          ))}
          <div>
            <label className="label">Date of Birth</label>
            <input type="date" className="input" value={patForm.date_of_birth || ''} onChange={setPat('date_of_birth')} />
          </div>
          <div>
            <label className="label">Gender</label>
            <select className="input" value={patForm.gender || ''} onChange={setPat('gender')}>
              <option value="">Select</option>
              <option>Male</option><option>Female</option><option>Other</option>
            </select>
          </div>
          <div>
            <label className="label">Blood Group</label>
            <select className="input" value={patForm.blood_group || ''} onChange={setPat('blood_group')}>
              <option value="">Select</option>
              {bloodGroups.map(bg => <option key={bg}>{bg}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Height (cm)</label><input type="number" className="input" value={patForm.height_cm || ''} onChange={setPat('height_cm')} /></div>
            <div><label className="label">Weight (kg)</label><input type="number" className="input" value={patForm.weight_kg || ''} onChange={setPat('weight_kg')} /></div>
          </div>
        </div>

        {/* Medical Info */}
        <div className="card space-y-4">
          <h2 className="section-title">Medical Information</h2>
          {[
            { label: 'Known Allergies',        key: 'known_allergies',        rows: 2 },
            { label: 'Chronic Conditions',     key: 'chronic_conditions',     rows: 2 },
            { label: 'Current Medications',    key: 'current_medications',    rows: 2 },
            { label: 'Family Medical History', key: 'family_medical_history', rows: 2 },
          ].map(f => (
            <div key={f.key}>
              <label className="label">{f.label}</label>
              <textarea rows={f.rows} className="input resize-none" value={patForm[f.key] || ''} onChange={setPat(f.key)} />
            </div>
          ))}
        </div>

        {/* Address */}
        <div className="card space-y-4">
          <h2 className="section-title">Address</h2>
          {[
            { label: 'Address',   key: 'address'  },
            { label: 'City',      key: 'city'     },
            { label: 'State',     key: 'state'    },
            { label: 'Pincode',   key: 'pincode'  },
            { label: 'Country',   key: 'country'  },
          ].map(f => (
            <div key={f.key}>
              <label className="label">{f.label}</label>
              <input className="input" value={patForm[f.key] || ''} onChange={setPat(f.key)} />
            </div>
          ))}
        </div>

        {/* Insurance */}
        <div className="card space-y-4">
          <h2 className="section-title">Insurance & Other</h2>
          {[
            { label: 'Occupation',          key: 'occupation'          },
            { label: 'Marital Status',      key: 'marital_status'      },
            { label: 'Insurance Provider',  key: 'insurance_provider'  },
            { label: 'Insurance ID',        key: 'insurance_id'        },
          ].map(f => (
            <div key={f.key}>
              <label className="label">{f.label}</label>
              <input className="input" value={patForm[f.key] || ''} onChange={setPat(f.key)} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
