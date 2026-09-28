import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FileText, AlertTriangle, CheckCircle, HelpCircle, Edit2, Save, Volume2 } from 'lucide-react';
import { reportsAPI } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import StatusBadge from '../../components/ui/StatusBadge';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';

function ValueRow({ value, onCorrect, language }) {
  const [editing, setEditing] = useState(false);
  const [newVal, setNewVal]   = useState(value.result);

  const save = async () => {
    try {
      await reportsAPI.correctValue(value.report_id || 0, value.id, newVal);
      toast.success('Value corrected');
      setEditing(false);
    } catch { toast.error('Failed to correct value'); }
  };

  const colors = { normal: 'border-green-200 bg-green-50 dark:bg-green-900/10', attention: 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/10', abnormal: 'border-red-200 bg-red-50 dark:bg-red-900/10' };
  const icons  = { normal: <CheckCircle className="w-4 h-4 text-green-500" />, attention: <AlertTriangle className="w-4 h-4 text-yellow-500" />, abnormal: <AlertTriangle className="w-4 h-4 text-red-500" /> };

  return (
    <div className={`border rounded-lg p-4 ${colors[value.status] || 'border-gray-200 bg-gray-50 dark:bg-gray-700'}`}>
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          {icons[value.status] || <HelpCircle className="w-4 h-4 text-gray-400" />}
          <span className="font-semibold text-gray-800 dark:text-gray-200 text-sm">{value.test_name}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <StatusBadge status={value.status} />
          {value.is_manually_corrected && <span className="text-xs text-blue-600 font-medium">Corrected</span>}
          <button onClick={() => setEditing(!editing)} className="p-1 rounded hover:bg-white/50" title="Correct value">
            <Edit2 className="w-3 h-3 text-gray-500" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4 mb-2">
        {editing ? (
          <div className="flex items-center gap-2">
            <input className="input w-28 text-sm py-1" value={newVal} onChange={e => setNewVal(e.target.value)} />
            <span className="text-sm text-gray-500">{value.unit}</span>
            <button onClick={save} className="btn-primary py-1 px-2 text-xs"><Save className="w-3 h-3" /></button>
          </div>
        ) : (
          <div className="text-lg font-bold text-gray-900 dark:text-white">
            {value.result} <span className="text-sm font-normal text-gray-500">{value.unit}</span>
          </div>
        )}
        <div className="text-sm text-gray-500">
          Ref: <span className="font-medium">{value.reference_range_text}</span>
        </div>
      </div>

      {value.explanation && (
        <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">{value.explanation}</p>
      )}
    </div>
  );
}

export default function ExplainReportPage() {
  const { id }  = useParams();
  const { user } = useAuth();
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState(user?.preferred_language || 'en');

  const load = () => {
    reportsAPI.getDetail(id, language)
      .then(r => setData(r.data))
      .catch(() => toast.error('Report not found'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [id, language]);

  const speakSummary = () => {
    if (!data?.report?.summary) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(data.report.summary);
    u.lang = language === 'ta' ? 'ta-IN' : 'en-IN';
    window.speechSynthesis.speak(u);
  };

  if (loading) return <LoadingSpinner message="Analyzing report..." />;
  if (!data) return <div className="text-center py-20 text-gray-500">Report not found.</div>;

  const { report, values, disclaimer } = data;
  const abnormal  = values.filter(v => v.status === 'abnormal');
  const attention = values.filter(v => v.status === 'attention');
  const normal    = values.filter(v => v.status === 'normal');

  return (
    <div className="max-w-5xl space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <Link to="/reports" className="text-sm text-primary-600 hover:underline">← Back to Reports</Link>
          <h1 className="page-title mt-1">Explain My Report</h1>
        </div>
        <div className="flex items-center gap-2">
          <select className="input w-36 text-sm" value={language} onChange={e => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="ta">தமிழ்</option>
          </select>
          <button onClick={speakSummary} className="btn-secondary" title="Read summary aloud">
            <Volume2 className="w-4 h-4" /> Read
          </button>
        </div>
      </div>

      {/* Report meta */}
      <div className="card">
        <div className="flex items-start gap-4">
          <FileText className="w-10 h-10 text-primary-500 flex-shrink-0" />
          <div className="flex-1">
            <h2 className="font-semibold text-gray-900 dark:text-white capitalize text-lg">
              {report.report_type?.replace(/_/g, ' ')}
            </h2>
            <p className="text-sm text-gray-500">{report.lab_name} · {report.report_date ? new Date(report.report_date).toLocaleDateString() : ''}</p>
            {report.ocr_confidence < 0.7 && (
              <div className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-1.5">
                ⚠️ OCR confidence is low ({(report.ocr_confidence * 100).toFixed(0)}%). Please verify extracted values manually.
              </div>
            )}
          </div>
          <div className="flex gap-2 text-center flex-shrink-0">
            {[['abnormal', abnormal.length, 'bg-red-100 text-red-700'], ['attention', attention.length, 'bg-yellow-100 text-yellow-700'], ['normal', normal.length, 'bg-green-100 text-green-700']].map(([s, c, cls]) => (
              <div key={s} className={`px-3 py-2 rounded-lg text-sm font-medium capitalize ${cls}`}>
                <div className="text-xl font-bold">{c}</div>
                <div className="text-xs">{s}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summary */}
      {report.summary && (
        <div className="card border-primary-200 dark:border-primary-800 bg-primary-50 dark:bg-primary-900/10">
          <h3 className="font-semibold text-primary-800 dark:text-primary-300 mb-2">AI-Generated Summary</h3>
          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{report.summary}</p>
        </div>
      )}

      {/* Values */}
      <div>
        <h2 className="section-title">Test Results ({values.length})</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {values.map(v => (
            <ValueRow key={v.id} value={{ ...v, report_id: id }} language={language} onCorrect={load} />
          ))}
        </div>
      </div>

      {/* Doctor questions */}
      {report.questions_for_doctor?.length > 0 && (
        <div className="card border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/10">
          <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-3 flex items-center gap-2">
            <HelpCircle className="w-4 h-4" /> Questions to Ask Your Doctor
          </h3>
          <ul className="space-y-2">
            {report.questions_for_doctor.map((q, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                <span className="w-5 h-5 bg-blue-200 dark:bg-blue-800 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">{i + 1}</span>
                {q}
              </li>
            ))}
          </ul>
        </div>
      )}

      <DisclaimerBox text={disclaimer} />
    </div>
  );
}
