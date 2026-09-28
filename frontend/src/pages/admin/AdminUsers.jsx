import React, { useEffect, useState } from 'react';
import { Users, Search, UserCheck, UserX, Filter } from 'lucide-react';
import { adminAPI } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

export default function AdminUsers() {
  const [users, setUsers]     = useState([]);
  const [total, setTotal]     = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch]   = useState('');
  const [role, setRole]       = useState('');

  const load = () => {
    adminAPI.listUsers({ search: search || undefined, role: role || undefined })
      .then(r => { setUsers(r.data.users || []); setTotal(r.data.total || 0); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, [search, role]);

  const toggle = async (id) => {
    try { await adminAPI.toggleUserActive(id); toast.success('Status updated'); load(); }
    catch { toast.error('Failed'); }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <div><h1 className="page-title">User Management</h1><p className="text-sm text-gray-500">{total} users total</p></div>
      </div>
      <div className="card flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input className="input pl-9" placeholder="Search by name or email..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select className="input w-36" value={role} onChange={e => setRole(e.target.value)}>
            <option value="">All Roles</option><option value="patient">Patient</option><option value="doctor">Doctor</option><option value="admin">Admin</option>
          </select>
        </div>
      </div>
      {loading ? <LoadingSpinner /> : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-gray-200 dark:border-gray-700">
              {['Name', 'Email', 'Role', 'Status', 'Created', 'Actions'].map(h => (
                <th key={h} className="text-left py-3 px-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr></thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="py-3 px-2 font-medium text-gray-900 dark:text-white">{u.full_name}</td>
                  <td className="py-3 px-2 text-gray-500">{u.email}</td>
                  <td className="py-3 px-2"><span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : u.role === 'doctor' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>{u.role}</span></td>
                  <td className="py-3 px-2"><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{u.is_active ? 'Active' : 'Inactive'}</span></td>
                  <td className="py-3 px-2 text-gray-400">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="py-3 px-2">
                    <button onClick={() => toggle(u.id)} className={`flex items-center gap-1 text-xs px-2 py-1 rounded font-medium transition-colors ${u.is_active ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-green-50 text-green-600 hover:bg-green-100'}`}>
                      {u.is_active ? <><UserX className="w-3 h-3" />Deactivate</> : <><UserCheck className="w-3 h-3" />Activate</>}
                    </button>
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
