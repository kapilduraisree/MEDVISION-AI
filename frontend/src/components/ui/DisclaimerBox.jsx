import React from 'react';
import { AlertTriangle, AlertCircle } from 'lucide-react';

export function DisclaimerBox({ text }) {
  return (
    <div className="disclaimer-box">
      <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
      <p>{text || '⚠️ This is AI-generated information for educational purposes only. Always consult a qualified healthcare professional before making any medical decisions.'}</p>
    </div>
  );
}

export function EmergencyBox({ text }) {
  return (
    <div className="emergency-box">
      <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-600" />
      <div>
        <p className="font-bold text-red-700 dark:text-red-400 mb-1">Emergency Alert</p>
        <p className="text-sm">{text || '🚨 This may require urgent medical attention. Call 112 (India) or your local emergency number immediately.'}</p>
      </div>
    </div>
  );
}
