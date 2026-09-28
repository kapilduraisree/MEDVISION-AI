import React from 'react';

const CONFIG = {
  normal:    { cls: 'badge-normal',    label: 'Normal' },
  attention: { cls: 'badge-attention', label: 'Attention' },
  abnormal:  { cls: 'badge-abnormal',  label: 'Abnormal' },
  unknown:   { cls: 'badge-unknown',   label: 'Unknown' },
  taken:     { cls: 'badge-normal',    label: 'Taken' },
  skipped:   { cls: 'badge-attention', label: 'Skipped' },
  missed:    { cls: 'badge-abnormal',  label: 'Missed' },
  confirmed: { cls: 'badge-normal',    label: 'Confirmed' },
  requested: { cls: 'badge-attention', label: 'Requested' },
  completed: { cls: 'badge-normal',    label: 'Completed' },
  cancelled: { cls: 'badge-abnormal',  label: 'Cancelled' },
};

export default function StatusBadge({ status }) {
  const cfg = CONFIG[status?.toLowerCase()] || CONFIG.unknown;
  return <span className={cfg.cls}>{cfg.label}</span>;
}
