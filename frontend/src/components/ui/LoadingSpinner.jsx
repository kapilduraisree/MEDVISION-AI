import React from 'react';

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <div className="spinner" />
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  );
}

export function PageLoader() {
  return (
    <div className="fixed inset-0 bg-white dark:bg-gray-950 flex items-center justify-center z-50">
      <div className="text-center">
        <div className="spinner w-10 h-10 border-4 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-400 font-medium">Loading MedVision AI...</p>
      </div>
    </div>
  );
}
