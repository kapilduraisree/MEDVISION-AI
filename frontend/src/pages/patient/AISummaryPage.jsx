import React, { useState } from 'react';
import { Zap, Volume2, Download, AlertTriangle } from 'lucide-react';
import { aiSummaryAPI } from '../../services/api';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

export default function AISummaryPage() {
  const { user } = useAuth();
  const [language, setLanguage] = useState(user?.preferred_language || 'en');
  const [generating, setGenerating] = useState(false);
  const [summary, setSummary]       = useState(null);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await aiSummaryAPI.generate({ language });
      setSummary(res.data);
    } catch { toast.error('Failed to generate summary'); }
    finally { setGenerating(false); }
  };

  const speakSummary = () => {
    if (!summary?.full_text) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(summary.full_text.replace(/[#*]/g, ''));
    u.lang = language === 'ta' ? 'ta-IN' : 'en-IN';
    window.speechSynthesis.speak(u);
  };

  const downloadSummary = () => {
    if (!summary?.full_text) return;
    const blob = new Blob([summary.full_text], { type: 'text/plain' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a'); a.href = url; a.download = 'health_summary.txt'; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Generate Health Summary</h1>
          <p className="text-sm text-gray-500 mt-1">AI combines your reports, symptoms, and medications into one structured summary</p>
        </div>
      </div>

      <div className="card space-y-5">
        <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-xl">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-amber-800 dark:text-amber-300">
              <p className="font-semibold mb-1">About this feature</p>
              <p>This AI summary is generated from your uploaded reports, symptoms, and medication data for <strong>informational purposes only</strong>. It does not constitute a medical diagnosis or treatment plan. Always consult your doctor.</p>
            </div>
          </div>
        </div>

        <div>
          <label className="label">Summary Language</label>
          <div className="flex gap-3 mt-1">
            {[{ val: 'en', label: '🇬🇧 English' }, { val: 'ta', label: '🇮🇳 தமிழ்' }].map(l => (
              <button key={l.val} onClick={() => setLanguage(l.val)}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${language === l.val ? 'bg-primary-600 text-white border-primary-600' : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50'}`}>
                {l.label}
              </button>
            ))}
          </div>
        </div>

        <button onClick={handleGenerate} disabled={generating} className="btn-primary w-full justify-center py-3 text-base">
          {generating ? <><span className="spinner" /> Generating AI Summary...</> : <><Zap className="w-5 h-5" /> Generate Health Summary</>}
        </button>
      </div>

      {summary && (
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="section-title mb-0">Your Health Summary</h2>
            <div className="flex items-center gap-2">
              <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium">AI Generated</span>
              <button onClick={speakSummary} className="btn-secondary py-1.5 text-sm">
                <Volume2 className="w-4 h-4" /> Read
              </button>
              <button onClick={downloadSummary} className="btn-secondary py-1.5 text-sm">
                <Download className="w-4 h-4" /> Save
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {Object.entries(summary.sections || {}).map(([key, content]) => {
              const titles = { symptoms: 'Symptoms', report_findings: 'Report Findings', medications: 'Current Medications', warnings: 'Warnings', historical_changes: 'Historical Changes', questions_for_doctor: 'Questions for Doctor', recommended_followup: 'Recommended Follow-up' };
              return (
                <div key={key} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-2 text-sm uppercase tracking-wide">
                    {titles[key] || key}
                  </h3>
                  <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{content}</ReactMarkdown>
                  </div>
                </div>
              );
            })}
          </div>

          <DisclaimerBox text={summary.disclaimer} />
        </div>
      )}
    </div>
  );
}
