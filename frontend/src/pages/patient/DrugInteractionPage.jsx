import React, { useState } from 'react';
import { Plus, X, Zap, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { drugInteractionsAPI } from '../../services/api';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import toast from 'react-hot-toast';

const SEVERITY_CONFIG = {
  major:           { color: 'bg-red-100 text-red-800 border-red-300',    icon: '🔴', label: 'Major' },
  moderate:        { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: '🟡', label: 'Moderate' },
  minor:           { color: 'bg-green-100 text-green-800 border-green-300',  icon: '🟢', label: 'Minor' },
  contraindicated: { color: 'bg-red-200 text-red-900 border-red-400',    icon: '⛔', label: 'Contraindicated' },
};

export default function DrugInteractionPage() {
  const [input, setInput]       = useState('');
  const [medicines, setMedicines] = useState([]);
  const [checking, setChecking] = useState(false);
  const [result, setResult]     = useState(null);

  const addMedicine = () => {
    const m = input.trim();
    if (!m || medicines.includes(m)) return;
    setMedicines(prev => [...prev, m]);
    setInput('');
    setResult(null);
  };

  const removeMedicine = (m) => {
    setMedicines(prev => prev.filter(x => x !== m));
    setResult(null);
  };

  const handleCheck = async () => {
    if (medicines.length < 2) { toast.error('Add at least 2 medicines'); return; }
    setChecking(true);
    try {
      const res = await drugInteractionsAPI.check(medicines);
      setResult(res.data);
    } catch { toast.error('Check failed'); }
    finally { setChecking(false); }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Drug Interaction Checker</h1>
          <p className="text-sm text-gray-500 mt-1">Check for interactions between multiple medicines</p>
        </div>
      </div>

      <div className="card space-y-4">
        <h2 className="section-title">Add Medicines to Check</h2>
        <div className="flex gap-2">
          <input
            className="input flex-1"
            placeholder="Enter medicine name (e.g. Metformin, Aspirin...)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addMedicine())}
          />
          <button onClick={addMedicine} className="btn-primary"><Plus className="w-4 h-4" />Add</button>
        </div>

        {medicines.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {medicines.map(m => (
              <div key={m} className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200 rounded-full text-sm font-medium">
                {m}
                <button onClick={() => removeMedicine(m)} className="hover:text-primary-600">
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}

        <button onClick={handleCheck} disabled={checking || medicines.length < 2} className="btn-primary">
          {checking ? <><span className="spinner" /> Checking...</> : <><Zap className="w-4 h-4" /> Check Interactions</>}
        </button>
      </div>

      {result && (
        <div className="space-y-4">
          {/* Summary */}
          <div className={`card border-2 ${result.total_interactions > 0 ? 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/10' : 'border-green-300 bg-green-50 dark:bg-green-900/10'}`}>
            <div className="flex items-center gap-3">
              {result.total_interactions > 0
                ? <AlertTriangle className="w-8 h-8 text-yellow-600" />
                : <CheckCircle className="w-8 h-8 text-green-600" />}
              <div>
                <p className="font-bold text-lg text-gray-900 dark:text-white">
                  {result.total_interactions > 0
                    ? `${result.total_interactions} interaction(s) found`
                    : 'No known interactions found'}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Checked {result.medicines_checked?.length} medicines
                </p>
              </div>
            </div>
          </div>

          {/* Interactions */}
          {result.interactions_found?.map((ix, i) => {
            const cfg = SEVERITY_CONFIG[ix.severity?.toLowerCase()] || SEVERITY_CONFIG.minor;
            return (
              <div key={i} className={`card border ${cfg.color}`}>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-lg">{cfg.icon}</span>
                  <h3 className="font-bold text-gray-900 dark:text-white">{ix.drug_a} + {ix.drug_b}</h3>
                  <span className={`ml-auto text-xs font-bold px-2 py-1 rounded-full border ${cfg.color}`}>{cfg.label}</span>
                </div>
                {ix.effect && <p className="text-sm text-gray-700 dark:text-gray-300 mb-2"><strong>Effect:</strong> {ix.effect}</p>}
                {ix.mechanism && <p className="text-sm text-gray-600 dark:text-gray-400 mb-2"><strong>Mechanism:</strong> {ix.mechanism}</p>}
                {ix.recommended_action && (
                  <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-sm font-medium text-blue-800 dark:text-blue-300">
                      💡 Recommended Action: {ix.recommended_action}
                    </p>
                  </div>
                )}
              </div>
            );
          })}

          {/* Duplicate warnings */}
          {result.duplicate_warnings?.map((d, i) => (
            <div key={i} className="card border border-orange-300 bg-orange-50 dark:bg-orange-900/10">
              <div className="flex items-start gap-2">
                <Info className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-orange-800 dark:text-orange-300 text-sm">Possible Duplicate Active Ingredient</p>
                  <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
                    <strong>{d.medicine_a}</strong> and <strong>{d.medicine_b}</strong> both contain <strong>{d.active_ingredient}</strong>.
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{d.warning}</p>
                </div>
              </div>
            </div>
          ))}

          <DisclaimerBox text={result.disclaimer} />
        </div>
      )}
    </div>
  );
}
