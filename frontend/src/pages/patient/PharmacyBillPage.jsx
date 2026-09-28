import React, { useEffect, useState } from 'react';
import { ShoppingBag, Upload, TrendingUp, DollarSign } from 'lucide-react';
import { pharmacyBillsAPI } from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import FileUploadZone from '../../components/ui/FileUploadZone';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

export default function PharmacyBillPage() {
  const [bills, setBills]           = useState([]);
  const [monthly, setMonthly]       = useState([]);
  const [totalSpent, setTotalSpent] = useState(0);
  const [loading, setLoading]       = useState(true);
  const [file, setFile]             = useState(null);
  const [uploading, setUploading]   = useState(false);
  const [result, setResult]         = useState(null);

  const load = () => {
    Promise.all([
      pharmacyBillsAPI.list(),
      pharmacyBillsAPI.monthlyExpense(new Date().getFullYear()),
    ]).then(([b, m]) => {
      setBills(b.data.bills || []); setTotalSpent(b.data.total_spent || 0);
      setMonthly(m.data.monthly_expense || []);
    }).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const handleUpload = async () => {
    if (!file) { toast.error('Select a file'); return; }
    setUploading(true);
    const fd = new FormData(); fd.append('file', file);
    try {
      const res = await pharmacyBillsAPI.upload(fd);
      setResult(res.data); setFile(null); load();
      toast.success(`Bill analyzed! Total: ₹${res.data.total_amount}`);
    } catch { toast.error('Upload failed'); }
    finally { setUploading(false); }
  };

  return (
    <div className="max-w-5xl space-y-5 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Pharmacy Bills</h1>
          <p className="text-sm text-gray-500 mt-1">Track medicine expenses with OCR bill scanning</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card flex items-center gap-4">
          <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center"><DollarSign className="w-6 h-6 text-green-600" /></div>
          <div><p className="text-2xl font-bold text-gray-900 dark:text-white">₹{totalSpent.toFixed(2)}</p><p className="text-sm text-gray-500">Total Spent</p></div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center"><ShoppingBag className="w-6 h-6 text-blue-600" /></div>
          <div><p className="text-2xl font-bold text-gray-900 dark:text-white">{bills.length}</p><p className="text-sm text-gray-500">Total Bills</p></div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center"><TrendingUp className="w-6 h-6 text-purple-600" /></div>
          <div><p className="text-2xl font-bold text-gray-900 dark:text-white">₹{bills.length ? (totalSpent / bills.length).toFixed(0) : 0}</p><p className="text-sm text-gray-500">Avg Per Bill</p></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Upload */}
        <div className="card space-y-4">
          <h2 className="section-title flex items-center gap-2"><Upload className="w-4 h-4" />Scan Pharmacy Bill</h2>
          <FileUploadZone onFile={setFile} label="Drop pharmacy bill here" hint="JPG, PNG, PDF" />
          <button onClick={handleUpload} disabled={uploading || !file} className="btn-primary w-full justify-center">
            {uploading ? <><span className="spinner" /> Scanning...</> : <><Upload className="w-4 h-4" /> Scan & Extract</>}
          </button>
          {result && (
            <div className="p-3 bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800 rounded-lg">
              <p className="font-semibold text-green-700 dark:text-green-400">{result.pharmacy_name}</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">Total: ₹{result.total_amount}</p>
              <div className="mt-2 space-y-1">
                {result.items?.map((item, i) => (
                  <div key={i} className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>{item.medicine_name} × {item.quantity}</span>
                    <span>₹{item.total_price}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Monthly chart */}
        <div className="card">
          <h2 className="section-title">Monthly Expenses {new Date().getFullYear()}</h2>
          {monthly.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={monthly} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={v => [`₹${v}`, 'Amount']} />
                <Bar dataKey="amount" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-gray-400"><TrendingUp className="w-10 h-10 mx-auto mb-2 opacity-40" /><p className="text-sm">No expense data yet</p></div>
          )}
        </div>
      </div>

      {/* Bills list */}
      {loading ? <LoadingSpinner /> : bills.length > 0 && (
        <div className="card">
          <h2 className="section-title">All Bills</h2>
          <div className="space-y-2">
            {bills.map(b => (
              <div key={b.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                <div>
                  <p className="font-medium text-sm text-gray-800 dark:text-gray-200">{b.pharmacy_name || 'Pharmacy'}</p>
                  <p className="text-xs text-gray-500">{b.bill_date ? new Date(b.bill_date).toLocaleDateString() : ''} · {b.item_count} items</p>
                </div>
                <span className="font-bold text-gray-900 dark:text-white">₹{b.total_amount?.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
