import React, { useState } from 'react';
import { Search, Pill, AlertTriangle, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { medicinesAPI } from '../../services/api';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';

function MedicineCard({ m }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-left">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <Pill className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900 dark:text-white">{m.brand_name}</p>
            <p className="text-xs text-gray-500">{m.generic_name} · {m.drug_category}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {m.is_otc && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">OTC</span>}
          {m.requires_prescription && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Rx</span>}
          {open ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
        </div>
      </button>
      {open && (
        <div className="p-4 space-y-4 bg-white dark:bg-gray-800">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { icon: Info,          label: 'General Purpose',     val: m.general_purpose },
              { icon: AlertTriangle, label: 'Precautions',          val: m.common_precautions },
              { icon: Info,          label: 'Common Side Effects',  val: m.common_side_effects },
              { icon: Info,          label: 'Storage',              val: m.storage_information },
            ].filter(f => f.val).map(({ label, val }) => (
              <div key={label} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{label}</p>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{val}</p>
              </div>
            ))}
          </div>
          {m.important_warnings && (
            <div className="p-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-xs font-semibold text-red-700 dark:text-red-400 mb-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Important Warnings
              </p>
              <p className="text-sm text-red-700 dark:text-red-300">{m.important_warnings}</p>
            </div>
          )}
          <div className="flex items-center gap-4 text-xs text-gray-400">
            {m.manufacturer && <span>By: {m.manufacturer}</span>}
            {m.is_verified && <span className="flex items-center gap-1 text-green-600">✓ Verified Database</span>}
            {m.source && <span>Source: {m.source}</span>}
          </div>
          <DisclaimerBox text={m.disclaimer || "This information is from the MedVision verified database. It is not a prescription. Always follow your doctor's advice."} />
        </div>
      )}
    </div>
  );
}

export default function MedicineInfoPage() {
  const [query, setQuery]     = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (query.trim().length < 2) return;
    setLoading(true); setSearched(true);
    try {
      const res = await medicinesAPI.search(query);
      setResults(res.data.results || []);
    } catch { setResults([]); }
    finally { setLoading(false); }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Medicine Information</h1>
          <p className="text-sm text-gray-500 mt-1">Search verified medicine database</p>
        </div>
      </div>
      <div className="card">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <input
              className="input pl-9"
              placeholder="Search by brand name, generic name, or active ingredient..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <span className="spinner" /> : <Search className="w-4 h-4" />}
            Search
          </button>
        </form>
      </div>
      {loading && <div className="text-center py-8 text-gray-400">Searching...</div>}
      {searched && !loading && results.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <Pill className="w-10 h-10 mx-auto mb-2 opacity-40" />
          <p>No medicines found for "{query}"</p>
        </div>
      )}
      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">{results.length} result(s) found</p>
          {results.map(m => <MedicineCard key={m.id} m={m} />)}
        </div>
      )}
      {!searched && (
        <div className="text-center py-16 text-gray-300 dark:text-gray-600">
          <Pill className="w-16 h-16 mx-auto mb-3" />
          <p className="text-sm">Search for a medicine to see detailed information</p>
          <p className="text-xs mt-1">Try: Metformin, Atorvastatin, Paracetamol...</p>
        </div>
      )}
    </div>
  );
}
