import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Upload, FileText, Eye, ChevronRight } from 'lucide-react';
import { reportsAPI } from '../../services/api';
import FileUploadZone from '../../components/ui/FileUploadZone';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import StatusBadge from '../../components/ui/StatusBadge';
import toast from 'react-hot-toast';

const REPORT_TYPES = [
  { val: 'blood_test',   label: 'Blood Test' },
  { val: 'urine_test',   label: 'Urine Test' },
  { val: 'lipid_profile',label: 'Lipid Profile' },
  { val: 'thyroid_test', label: 'Thyroid Test' },
  { val: 'xray',         label: 'X-Ray' },
  { val: 'scan',         label: 'Scan / Ultrasound' },
  { val: 'ecg',          label: 'ECG' },
  { val: 'other',        label: 'Other' },
];

export default function UploadReportPage() {
  const navigate  = useNavigate();
  const [file, setFile]           = useState(null);
  const [reportType, setReportType] = useState('blood_test');
  const [labName, setLabName]     = useState('');
  const [reportDate, setReportDate] = useState('');
  const [language, setLanguage]   = useState('en');
  const [uploading, setUploading] = useState(false);
  const [reports, setReports]     = useState([]);
  const [loadingReports, setLoadingReports] = useState(true);

  const loadReports = () => {
    reportsAPI.list().then(r => setReports(r.data.reports || [])).catch(() => {}).finally(() => setLoadingReports(false));
  };
  useEffect(() => { loadReports(); }, []);

  const handleUpload = async () => {
    if (!file) { toast.error('Please select a file'); return; }
    setUploading(true);
    const fd = new FormData();
    fd.append('file', file);
    fd.append('report_type', reportType);
    fd.append('lab_name', labName);
    fd.append('language', language);
    if (reportDate) fd.append('report_date', reportDate);

    try {
      const res = await reportsAPI.upload(fd);
      toast.success(`Report analyzed! ${res.data.values_extracted} values extracted.`);
      navigate(`/reports/${res.data.report_id}`);
    } catch {
      toast.error('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Medical Reports</h1>
          <p className="text-sm text-gray-500 mt-1">Upload and analyze your medical reports using AI</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload panel */}
        <div className="card space-y-5">
          <h2 className="section-title flex items-center gap-2"><Upload className="w-4 h-4" /> Upload New Report</h2>

          <FileUploadZone
            onFile={setFile}
            accept={{ 'image/*': [], 'application/pdf': [] }}
            label="Drop your report here"
            hint="PDF, JPG, PNG supported"
          />

          <div>
            <label className="label">Report Type</label>
            <select className="input" value={reportType} onChange={e => setReportType(e.target.value)}>
              {REPORT_TYPES.map(t => <option key={t.val} value={t.val}>{t.label}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Lab / Hospital Name</label>
            <input className="input" placeholder="e.g. City Diagnostics" value={labName} onChange={e => setLabName(e.target.value)} />
          </div>
          <div>
            <label className="label">Report Date</label>
            <input type="date" className="input" value={reportDate} onChange={e => setReportDate(e.target.value)} />
          </div>
          <div>
            <label className="label">Explanation Language</label>
            <select className="input" value={language} onChange={e => setLanguage(e.target.value)}>
              <option value="en">English</option>
              <option value="ta">தமிழ் (Tamil)</option>
            </select>
          </div>

          <button onClick={handleUpload} disabled={uploading || !file} className="btn-primary w-full justify-center py-3">
            {uploading ? (
              <><span className="spinner" /> Analyzing report...</>
            ) : (
              <><Upload className="w-4 h-4" /> Upload &amp; Analyze</>
            )}
          </button>
          <DisclaimerBox />
        </div>

        {/* Reports list */}
        <div className="card">
          <h2 className="section-title flex items-center gap-2"><FileText className="w-4 h-4" /> Previous Reports</h2>
          {loadingReports ? <LoadingSpinner /> : reports.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <FileText className="w-10 h-10 mx-auto mb-2 opacity-40" />
              <p className="text-sm">No reports uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
              {reports.map(r => (
                <Link key={r.id} to={`/reports/${r.id}`}
                  className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/10 transition-colors">
                  <div className="flex items-center gap-3">
                    <FileText className="w-8 h-8 text-primary-400 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-gray-800 dark:text-gray-200 capitalize">
                        {r.report_type?.replace(/_/g, ' ')}
                      </p>
                      <p className="text-xs text-gray-500">{r.lab_name || '—'} · {new Date(r.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {r.is_doctor_reviewed && <span className="text-xs text-green-600 font-medium">Reviewed</span>}
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
