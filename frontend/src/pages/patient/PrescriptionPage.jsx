import React, { useEffect, useState } from 'react';
import { Syringe, Upload, CheckCircle, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { prescriptionsAPI } from '../../services/api';
import FileUploadZone from '../../components/ui/FileUploadZone';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import toast from 'react-hot-toast';

function PrescriptionCard({ rx }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
      >
        <div className="flex items-center gap-3 text-left">
          <Syringe className="w-5 h-5 text-primary-500" />
          <div>
            <p className="font-medium text-sm text-gray-800 dark:text-gray-200">
              Prescription · {new Date(rx.created_at).toLocaleDateString()}
            </p>
            <p className="text-xs text-gray-500">{rx.item_count} medicine(s) extracted</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {rx.is_user_verified
            ? <span className="text-xs text-green-600 font-medium flex items-center gap-1"><CheckCircle className="w-3 h-3" />Verified</span>
            : <span className="text-xs text-amber-600 font-medium">Needs Verification</span>}
          {open ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
        </div>
      </button>
      {open && <PrescriptionDetail id={rx.id} />}
    </div>
  );
}

function PrescriptionDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    prescriptionsAPI.getOne(id).then(r => setData(r.data)).catch(() => {});
  }, [id]);
  if (!data) return <div className="p-4"><LoadingSpinner /></div>;

  const verify = async () => {
    try { await prescriptionsAPI.verify(id); toast.success('Marked as verified'); }
    catch { toast.error('Failed'); }
  };

  return (
    <div className="p-4 space-y-4">
      <div className="disclaimer-box">
        <AlertTriangle className="w-4 h-4 flex-shrink-0" />
        <p className="text-xs">{data.disclaimer}</p>
      </div>
      <div className="space-y-3">
        {data.items.map(item => (
          <div key={item.id} className={`p-3 rounded-lg border ${item.needs_verification ? 'border-amber-300 bg-amber-50 dark:bg-amber-900/10' : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'}`}>
            {item.needs_verification && (
              <p className="text-xs text-amber-700 dark:text-amber-400 font-medium mb-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Please verify with your doctor/pharmacist
              </p>
            )}
            <p className="font-semibold text-sm text-gray-900 dark:text-white">{item.medicine_name}</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2 text-xs text-gray-600 dark:text-gray-400">
              {item.strength && <span>Strength: <strong>{item.strength}</strong></span>}
              {item.frequency && <span>Frequency: <strong>{item.frequency}</strong></span>}
              {item.duration && <span>Duration: <strong>{item.duration}</strong></span>}
              {item.before_after_food && <span>Food: <strong className="capitalize">{item.before_after_food}</strong></span>}
              {item.dosage_instruction && <span className="col-span-2">Instructions: <strong>{item.dosage_instruction}</strong></span>}
              {item.doctor_notes && <span className="col-span-2">Doctor notes: <strong>{item.doctor_notes}</strong></span>}
            </div>
          </div>
        ))}
      </div>
      {!data.prescription?.is_user_verified && (
        <button onClick={verify} className="btn-primary">
          <CheckCircle className="w-4 h-4" /> Mark as Verified
        </button>
      )}
    </div>
  );
}

export default function PrescriptionPage() {
  const [file, setFile]           = useState(null);
  const [uploading, setUploading] = useState(false);
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading]     = useState(true);

  const load = () => {
    prescriptionsAPI.list().then(r => setPrescriptions(r.data.prescriptions || [])).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const handleUpload = async () => {
    if (!file) { toast.error('Select a file first'); return; }
    setUploading(true);
    const fd = new FormData(); fd.append('file', file);
    try {
      await prescriptionsAPI.upload(fd);
      toast.success('Prescription analyzed!');
      setFile(null);
      load();
    } catch { toast.error('Upload failed'); }
    finally { setUploading(false); }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Prescription Analyzer</h1>
          <p className="text-sm text-gray-500 mt-1">Upload prescription images to extract medicine details</p>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card space-y-4">
          <h2 className="section-title flex items-center gap-2"><Upload className="w-4 h-4" />Upload Prescription</h2>
          <FileUploadZone onFile={setFile} label="Drop prescription image here" hint="JPG, PNG, PDF" />
          <button onClick={handleUpload} disabled={uploading || !file} className="btn-primary w-full justify-center">
            {uploading ? <><span className="spinner" /> Analyzing...</> : <><Syringe className="w-4 h-4" /> Analyze Prescription</>}
          </button>
          <DisclaimerBox text="Extracted information may contain errors, especially for handwritten prescriptions. Always verify with your doctor or pharmacist before taking any medication." />
        </div>
        <div className="card">
          <h2 className="section-title">Previous Prescriptions ({prescriptions.length})</h2>
          {loading ? <LoadingSpinner /> : prescriptions.length === 0 ? (
            <div className="text-center py-10 text-gray-400"><Syringe className="w-10 h-10 mx-auto mb-2 opacity-40" /><p className="text-sm">No prescriptions uploaded yet</p></div>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
              {prescriptions.map(rx => <PrescriptionCard key={rx.id} rx={rx} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
