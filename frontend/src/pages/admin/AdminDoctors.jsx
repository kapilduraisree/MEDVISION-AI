import React, { useEffect, useState } from 'react';
import { Stethoscope, CheckCircle, XCircle } from 'lucide-react';
import { adminAPI } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

export default function AdminDoctors() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    adminAPI.listDoctors().then(r => setDoctors(r.data.doctors || [])).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const verify = async (id) => {
    try { await adminAPI.verifyDoctor(id); toast.success('Doctor verified'); load(); }
    catch { toast.error('Failed'); }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <div><h1 className="page-title">Doctor Management</h1><p className="text-sm text-gray-500">{doctors.length} doctors</p></div>
      </div>
      {loading ? <LoadingSpinner /> : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-gray-200 dark:border-gray-700">
              {['Name', 'Specialization', 'Registration', 'Verified', 'Available', 'Actions'].map(h => (
                <th key={h} className="text-left py-3 px-2 text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr></thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {doctors.map(d => (
                <tr key={d.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="py-3 px-2 font-medium text-gray-900 dark:text-white">{d.name}</td>
                  <td className="py-3 px-2 text-gray-500">{d.specialization || '—'}</td>
                  <td className="py-3 px-2 text-gray-500">{d.registration_number || '—'}</td>
                  <td className="py-3 px-2">{d.is_verified ? <CheckCircle className="w-4 h-4 text-green-500" /> : <XCircle className="w-4 h-4 text-red-400" />}</td>
                  <td className="py-3 px-2">{d.is_available ? <span className="text-green-600 text-xs">Yes</span> : <span className="text-red-500 text-xs">No</span>}</td>
                  <td className="py-3 px-2">
                    {!d.is_verified && (
                      <button onClick={() => verify(d.id)} className="flex items-center gap-1 text-xs px-2 py-1 rounded bg-green-50 text-green-600 hover:bg-green-100 font-medium">
                        <CheckCircle className="w-3 h-3" /> Verify
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
