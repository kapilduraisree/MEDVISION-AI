import React from 'react';
import { Link } from 'react-router-dom';
import {
  Heart, FileText, Pill, MessageSquare, TrendingUp, Shield,
  Mic, Camera, Globe, ChevronRight, CheckCircle, AlertTriangle
} from 'lucide-react';

const features = [
  { icon: FileText,     title: 'OCR Report Analyzer',      desc: 'Upload blood reports, X-rays and scans. AI extracts values and explains them in plain language.' },
  { icon: Pill,         title: 'Medicine Intelligence',     desc: 'Scan medicine strips, check drug interactions, and manage your medication schedule.' },
  { icon: Mic,          title: 'Voice Input',               desc: 'Describe symptoms in English or Tamil using voice. AI transcribes and processes your input.' },
  { icon: Camera,       title: 'Prescription Analyzer',     desc: 'Upload prescription images. Extract medicine names, dosage and instructions automatically.' },
  { icon: TrendingUp,   title: 'Health Trends',             desc: 'Track glucose, cholesterol, hemoglobin and more. View trends over time with interactive charts.' },
  { icon: MessageSquare,title: 'AI Health Assistant',       desc: 'Ask health questions in Tamil or English. Get educational explanations with professional guidance.' },
  { icon: Globe,        title: 'Tamil & English Support',   desc: 'Full bilingual support for Tamil and English across the entire platform.' },
  { icon: Shield,       title: 'Secure Medical Locker',     desc: 'Store all your medical documents safely. Lab reports, prescriptions, bills – all in one place.' },
];

const roles = [
  { role: 'Patient',  color: 'bg-blue-600',   points: ['Upload reports & prescriptions', 'Track medicines & reminders', 'View health trends', 'AI-powered explanations'] },
  { role: 'Doctor',   color: 'bg-green-600',  points: ['Review patient reports', 'Add clinical notes', 'Approve AI summaries', 'Manage appointments'] },
  { role: 'Admin',    color: 'bg-purple-600', points: ['Manage users & doctors', 'Medicine database management', 'System analytics', 'Audit logs'] },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-950">
      {/* Nav */}
      <nav className="sticky top-0 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Heart className="w-7 h-7 text-primary-600" />
            <span className="font-bold text-xl text-primary-600">MedVision AI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login"    className="btn-secondary text-sm">Login</Link>
            <Link to="/register" className="btn-primary text-sm">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-blue-800 text-white py-24 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/20 rounded-full text-sm font-medium mb-6">
            <AlertTriangle className="w-4 h-4" />
            <span>For educational & informational use — Not a substitute for medical advice</span>
          </div>
          <h1 className="text-5xl font-extrabold mb-6 leading-tight">
            MedVision AI<br />
            <span className="text-blue-200">Health Report Analysis</span>
          </h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto mb-10">
            Upload your medical reports, prescriptions and medicine strips.
            Get AI-powered explanations in Tamil & English to understand your health better.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-700 rounded-xl font-bold text-lg hover:bg-blue-50 transition-colors">
              Start Free <ChevronRight className="w-5 h-5" />
            </Link>
            <Link to="/login" className="inline-flex items-center gap-2 px-8 py-4 bg-white/20 text-white rounded-xl font-bold text-lg hover:bg-white/30 transition-colors">
              Demo Login
            </Link>
          </div>
          <p className="mt-6 text-blue-200 text-sm">
            Demo: patient@medvision.ai / doctor@medvision.ai / admin@medvision.ai · Password: Password@123
          </p>
        </div>
      </section>

      {/* Disclaimer Banner */}
      <div className="bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-700 py-3 px-6">
        <p className="max-w-5xl mx-auto text-center text-sm text-amber-800 dark:text-amber-300 font-medium">
          ⚠️ MedVision AI is an informational tool designed to help patients understand their health reports.
          It does NOT diagnose diseases or prescribe medications. Always consult a qualified doctor for medical decisions.
        </p>
      </div>

      {/* Features */}
      <section className="py-20 px-6 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-3">
            Everything you need to understand your health
          </h2>
          <p className="text-center text-gray-500 dark:text-gray-400 mb-12">Powered by AI · Bilingual · Secure</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="card hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{title}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Roles */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Built for every stakeholder
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {roles.map(({ role, color, points }) => (
              <div key={role} className="card border-0 shadow-md">
                <div className={`inline-block px-4 py-1.5 ${color} text-white text-sm font-bold rounded-full mb-4`}>
                  {role}
                </div>
                <ul className="space-y-3">
                  {points.map(p => (
                    <li key={p} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      {p}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-6 bg-primary-600 text-white text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to understand your health reports?</h2>
        <p className="text-blue-100 mb-8 text-lg">Free for college project demo. Tamil & English supported.</p>
        <Link to="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-700 rounded-xl font-bold text-lg hover:bg-blue-50 transition-colors">
          Create Account <ChevronRight className="w-5 h-5" />
        </Link>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 bg-gray-900 text-gray-400 text-center text-sm">
        <p>© 2026 MedVision AI · Final Year Project · For educational purposes only</p>
        <p className="mt-1 text-xs text-gray-500">
          All AI-generated information must be verified by a qualified healthcare professional before any clinical use.
        </p>
      </footer>
    </div>
  );
}
