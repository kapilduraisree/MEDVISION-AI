import React, { useEffect, useState } from 'react';
import { FolderOpen, Upload, Search, Trash2, Eye, Filter } from 'lucide-react';
import { documentsAPI } from '../../services/api';
import FileUploadZone from '../../components/ui/FileUploadZone';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Modal from '../../components/ui/Modal';
import toast from 'react-hot-toast';

const CATEGORIES = [
  { val: '', label: 'All Documents' },
  { val: 'lab_report',    label: 'Lab Reports' },
  { val: 'prescription',  label: 'Prescriptions' },
  { val: 'scan_report',   label: 'Scan Reports' },
  { val: 'medicine_bill', label: 'Medicine Bills' },
  { val: 'doctor_note',   label: 'Doctor Notes' },
  { val: 'other',         label: 'Other' },
];

const FILE_ICONS = { pdf: '📄', jpg: '🖼️', jpeg: '🖼️', png: '🖼️', doc: '📝', docx: '📝' };

export default function MedicalLockerPage() {
  const [docs, setDocs]           = useState([]);
  const [total, setTotal]         = useState(0);
  const [loading, setLoading]     = useState(true);
  const [search, setSearch]       = useState('');
  const [category, setCategory]   = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [file, setFile]           = useState(null);
  const [form, setForm]           = useState({ title: '', category: 'lab_report', description: '', tags: '' });
  const [uploading, setUploading] = useState(false);

  const load = () => {
    documentsAPI.list({ category: category || undefined, search: search || undefined })
      .then(r => { setDocs(r.data.documents || []); setTotal(r.data.total || 0); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, [category, search]);

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) { toast.error('Select a file'); return; }
    setUploading(true);
    const fd = new FormData();
    fd.append('file', file);
    fd.append('title', form.title);
    fd.append('category', form.category);
    fd.append('description', form.description);
    fd.append('tags', form.tags);
    try {
      await documentsAPI.upload(fd);
      toast.success('Document uploaded');
      setShowUpload(false); setFile(null);
      setForm({ title: '', category: 'lab_report', description: '', tags: '' });
      load();
    } catch { toast.error('Upload failed'); }
    finally { setUploading(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this document?')) return;
    try { await documentsAPI.delete(id); toast.success('Deleted'); load(); }
    catch { toast.error('Failed to delete'); }
  };

  return (
    <div className="max-w-5xl space-y-5 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Medical Locker</h1>
          <p className="text-sm text-gray-500 mt-1">Secure storage for all your medical documents</p>
        </div>
        <button onClick={() => setShowUpload(true)} className="btn-primary">
          <Upload className="w-4 h-4" /> Upload Document
        </button>
      </div>

      {/* Filters */}
      <div className="card flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input className="input pl-9" placeholder="Search documents..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select className="input w-44" value={category} onChange={e => setCategory(e.target.value)}>
            {CATEGORIES.map(c => <option key={c.val} value={c.val}>{c.label}</option>)}
          </select>
        </div>
        <span className="text-sm text-gray-500 self-center">{total} document(s)</span>
      </div>

      {loading ? <LoadingSpinner /> : docs.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <FolderOpen className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No documents found</p>
          <p className="text-sm mt-1">Upload your medical documents to keep them organized</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {docs.map(doc => (
            <div key={doc.id} className="card hover:shadow-md transition-shadow group">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <span className="text-3xl">{FILE_ICONS[doc.file_type] || '📁'}</span>
                  <div className="min-w-0">
                    <p className="font-medium text-sm text-gray-900 dark:text-white truncate">{doc.title}</p>
                    <p className="text-xs text-gray-500 capitalize">{doc.category?.replace(/_/g, ' ')}</p>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <a href={`http://localhost:8000${doc.file_path}`} target="_blank" rel="noreferrer"
                    className="p-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 text-blue-500">
                    <Eye className="w-3.5 h-3.5" />
                  </a>
                  <button onClick={() => handleDelete(doc.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              {doc.description && <p className="text-xs text-gray-500 mt-2 line-clamp-2">{doc.description}</p>}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 text-xs text-gray-400">
                <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                <span>{doc.file_size_kb ? `${doc.file_size_kb} KB` : ''}</span>
              </div>
              {doc.tags && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {doc.tags.split(',').map(tag => (
                    <span key={tag} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded text-xs">{tag.trim()}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showUpload} onClose={() => setShowUpload(false)} title="Upload Document">
        <form onSubmit={handleUpload} className="space-y-4">
          <div><label className="label">Document Title *</label><input className="input" placeholder="e.g. Blood Test Report Sep 2026" value={form.title} onChange={set('title')} required /></div>
          <div>
            <label className="label">Category</label>
            <select className="input" value={form.category} onChange={set('category')}>
              {CATEGORIES.slice(1).map(c => <option key={c.val} value={c.val}>{c.label}</option>)}
            </select>
          </div>
          <FileUploadZone onFile={setFile} label="Drop document here" hint="PDF, JPG, PNG, DOC" />
          <div><label className="label">Description</label><input className="input" placeholder="Optional description" value={form.description} onChange={set('description')} /></div>
          <div><label className="label">Tags (comma separated)</label><input className="input" placeholder="diabetes, blood test, 2026" value={form.tags} onChange={set('tags')} /></div>
          <div className="flex gap-3">
            <button type="button" onClick={() => setShowUpload(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={uploading || !file} className="btn-primary flex-1 justify-center">
              {uploading ? <><span className="spinner" /> Uploading...</> : <><Upload className="w-4 h-4" /> Upload</>}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
