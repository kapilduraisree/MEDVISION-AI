import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Image } from 'lucide-react';

export default function FileUploadZone({
  onFile,
  accept = { 'image/*': [], 'application/pdf': [] },
  maxSizeMB = 20,
  label = 'Drop file here or click to upload',
  hint = 'Supports PDF, JPG, PNG',
  disabled = false,
}) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles[0]) onFile(acceptedFiles[0]);
  }, [onFile]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept,
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: false,
    disabled,
  });

  const file = acceptedFiles[0];
  const isImage = file && file.type.startsWith('image/');

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
        ${isDragActive
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700/30'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />
      {file ? (
        <div className="flex flex-col items-center gap-2">
          {isImage
            ? <Image className="w-10 h-10 text-primary-500" />
            : <FileText className="w-10 h-10 text-primary-500" />}
          <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{file.name}</p>
          <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
          <p className="text-xs text-primary-600">Click or drop to replace</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2">
          <Upload className="w-10 h-10 text-gray-400" />
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</p>
          <p className="text-xs text-gray-400">{hint} · Max {maxSizeMB}MB</p>
        </div>
      )}
    </div>
  );
}
