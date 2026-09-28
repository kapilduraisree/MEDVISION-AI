import React, { useState } from 'react';
import { Camera, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { medicinesAPI } from '../../services/api';
import FileUploadZone from '../../components/ui/FileUploadZone';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import toast from 'react-hot-toast';

export default function MedicineScanPage() {
  const [file, setFile]       = useState(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult]   = useState(null);

  const handleScan = async () => {
    if (!file) { toast.error('Select an image first'); return; }
    setScanning(true);
    const fd = new FormData(); fd.append('file', file);
    try {
      const res = await medicinesAPI.scanStrip(fd);
      setResult(res.data);
    } catch { toast.error('Scan failed. Please try again.'); }
    finally { setScanning(false); }
  };

  return (
    <div className="max-w-3xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Medicine Strip Scanner</h1>
          <p className="text-sm text-gray-500 mt-1">Scan medicine packaging to extract information</p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card space-y-4">
          <h2 className="section-title flex items-center gap-2"><Camera className="w-4 h-4" />Upload Medicine Image</h2>
          <FileUploadZone onFile={setFile} accept={{ 'image/*': [] }} label="Drop medicine strip photo here" hint="JPG, PNG only" />
          <button onClick={handleScan} disabled={scanning || !file} className="btn-primary w-full justify-center">
            {scanning ? <><span className="spinner" /> Scanning...</> : <><Camera className="w-4 h-4" /> Scan Medicine</>}
          </button>
          <DisclaimerBox text="This scanner extracts visible information from packaging only. Do not use this as a prescription or dosage recommendation." />
        </div>

        <div className="card">
          <h2 className="section-title">Scan Results</h2>
          {!result ? (
            <div className="text-center py-16 text-gray-400">
              <Camera className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm">Upload a medicine image to see extracted information</p>
            </div>
          ) : (
            <div className="space-y-4">
              {result.is_expired && (
                <div className="emergency-box">
                  <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-sm font-medium">{result.expiry_warning}</p>
                </div>
              )}
              {result.low_confidence && (
                <div className="disclaimer-box">
                  <Info className="w-4 h-4 flex-shrink-0" />
                  <p className="text-xs">Low confidence scan. Please verify information from the original packaging.</p>
                </div>
              )}
              <div className="space-y-3">
                {[
                  { label: 'Brand Name',        val: result.brand_name },
                  { label: 'Generic Name',       val: result.generic_name },
                  { label: 'Strength',           val: result.strength },
                  { label: 'Manufacturer',       val: result.manufacturer },
                  { label: 'Expiry Date',        val: result.expiry_date, warn: result.is_expired },
                  { label: 'Manufacturing Date', val: result.manufacturing_date },
                  { label: 'Batch Number',       val: result.batch_number },
                ].filter(f => f.val).map(({ label, val, warn }) => (
                  <div key={label} className={`flex justify-between items-center text-sm p-2 rounded ${warn ? 'bg-red-50 dark:bg-red-900/10' : 'bg-gray-50 dark:bg-gray-700'}`}>
                    <span className="text-gray-500">{label}</span>
                    <span className={`font-semibold ${warn ? 'text-red-600' : 'text-gray-800 dark:text-gray-200'}`}>
                      {val} {warn && '⚠️'}
                    </span>
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <div className="flex-1 h-2 bg-gray-200 rounded-full">
                  <div className="h-2 bg-primary-500 rounded-full" style={{ width: `${(result.confidence || 0) * 100}%` }} />
                </div>
                <span>Confidence: {((result.confidence || 0) * 100).toFixed(0)}%</span>
              </div>
              <DisclaimerBox text={result.disclaimer} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
