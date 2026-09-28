import React, { useEffect, useState } from 'react';
import { Shield, Search, RefreshCw } from 'lucide-react';
import { adminAPI } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

export default function AdminAuditLogs() {
  const [logs, setLogs]     = useState([]);
  const [total, setTotal]   = useState(0);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState('');

  const load = () => {
    adminAPI.getAuditLogs({ action: action || undefined })
      .then(r => { setLogs(r.data.logs || []); setTotal(r.data.total || 0); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, [action]);

  const ACTION_COLORS = {
    user_login:  'bg-green-100 text-green-700',
    user_logout: 'bg-gray-100 text-gray-600',
    user_register: 'bg-blue-100 text-blue-700',
    admin_toggle_user: 'bg-yellow-100 text-yellow-700',
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <div><h1 className="page-title">Audit Logs</h1><p className="text-sm text-gray-500">{total} entries</p></div>
        <button onClick={load} className="btn-secondary"><RefreshCw className="w-4 h-4" />Refresh</button>
      </div>
      <div className="card flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input className="input pl-9" placeholder="Filter by action..." value={action} onChange={e => setAction(e.target.value)} />
        </div>
      </div>
      {loading ? <LoadingSpinner /> : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-gray-200 dark:border-gray-700">
              {['#', 'User', 'Action', 'Entity', 'Status', 'Time'].map(h => (
                <th key={h} className="text-left py-3 px-2 text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr></thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {logs.map(l => (
                <tr key={l.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="py-2 px-2 text-gray-400 text-xs">{l.id}</td>
                  <td className="py-2 px-2 text-gray-600 dark:text-gray-400">{l.user_id || '—'}</td>
                  <td className="py-2 px-2"><span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ACTION_COLORS[l.action] || 'bg-gray-100 text-gray-600'}`}>{l.action}</span></td>
                  <td className="py-2 px-2 text-gray-500">{l.entity_type} {l.entity_id ? `#${l.entity_id}` : ''}</td>
                  <td className="py-2 px-2"><span className={`text-xs font-medium ${l.status === 'success' ? 'text-green-600' : 'text-red-500'}`}>{l.status}</span></td>
                  <td className="py-2 px-2 text-gray-400 text-xs">{new Date(l.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {logs.length === 0 && <div className="text-center py-8 text-gray-400"><Shield className="w-8 h-8 mx-auto mb-2 opacity-40" /><p className="text-sm">No audit logs found</p></div>}
        </div>
      )}
    </div>
  );
}
