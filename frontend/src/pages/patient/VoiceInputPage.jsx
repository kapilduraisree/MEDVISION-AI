import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2, Send, RefreshCw } from 'lucide-react';
import { symptomsAPI, voiceAPI } from '../../services/api';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import toast from 'react-hot-toast';

export default function VoiceInputPage() {
  const [recording, setRecording]   = useState(false);
  const [transcript, setTranscript] = useState('');
  const [language, setLanguage]     = useState('en');
  const [saving, setSaving]         = useState(false);
  const [speaking, setSpeaking]     = useState(false);
  const recognitionRef              = useRef(null);

  // Browser Web Speech API
  const startRecording = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Speech recognition not supported in this browser. Try Chrome.');
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SR();
    recognition.lang       = language === 'ta' ? 'ta-IN' : 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      const t = Array.from(event.results).map(r => r[0].transcript).join('');
      setTranscript(t);
    };
    recognition.onerror = () => {
      toast.error('Voice recognition failed. Please try again.');
      setRecording(false);
    };
    recognition.onend = () => setRecording(false);

    recognition.start();
    recognitionRef.current = recognition;
    setRecording(true);
    toast.success('Listening... Speak now');
  };

  const stopRecording = () => {
    recognitionRef.current?.stop();
    setRecording(false);
  };

  const handleSave = async () => {
    if (!transcript.trim()) { toast.error('Nothing to save'); return; }
    setSaving(true);
    try {
      const res = await symptomsAPI.add({
        description: transcript,
        input_method: 'voice',
        voice_transcript: transcript,
        language,
      });
      toast.success('Voice symptoms saved');
      if (res.data.is_emergency_flagged) {
        toast.error('⚠️ Emergency symptoms detected! Seek immediate medical care.', { duration: 8000 });
      }
    } catch {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const speakText = (text) => {
    if (!text) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'ta' ? 'ta-IN' : 'en-IN';
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="max-w-3xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Voice Input</h1>
          <p className="text-sm text-gray-500 mt-1">Speak your symptoms in English or Tamil</p>
        </div>
      </div>

      <div className="card space-y-6">
        {/* Language */}
        <div>
          <label className="label">Language / மொழி</label>
          <div className="flex gap-3 mt-1">
            {[{ val: 'en', label: '🇬🇧 English' }, { val: 'ta', label: '🇮🇳 தமிழ்' }].map(l => (
              <button
                key={l.val}
                onClick={() => setLanguage(l.val)}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${language === l.val ? 'bg-primary-600 text-white border-primary-600' : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50'}`}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>

        {/* Mic button */}
        <div className="flex flex-col items-center gap-4 py-8">
          <button
            onClick={recording ? stopRecording : startRecording}
            className={`w-24 h-24 rounded-full flex items-center justify-center shadow-lg transition-all transform hover:scale-105 ${
              recording ? 'bg-red-500 hover:bg-red-600 animate-pulse-slow' : 'bg-primary-600 hover:bg-primary-700'
            }`}
          >
            {recording ? <MicOff className="w-10 h-10 text-white" /> : <Mic className="w-10 h-10 text-white" />}
          </button>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {recording ? '🔴 Recording... Click to stop' : 'Click to start recording'}
          </p>
          {language === 'ta' && (
            <p className="text-xs text-gray-400">பேசுவதற்கு கிளிக் செய்யவும்</p>
          )}
        </div>

        {/* Transcript */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="label mb-0">Transcript</label>
            <div className="flex gap-2">
              <button
                onClick={() => speakText(transcript)}
                disabled={!transcript || speaking}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40"
                title="Play back"
              >
                <Volume2 className="w-4 h-4 text-gray-500" />
              </button>
              <button
                onClick={() => setTranscript('')}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                title="Clear"
              >
                <RefreshCw className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          </div>
          <textarea
            rows={5} className="input resize-none"
            placeholder={language === 'ta' ? 'குரல் உரை இங்கே தோன்றும்...' : 'Voice transcript will appear here...'}
            value={transcript}
            onChange={e => setTranscript(e.target.value)}
          />
          <p className="text-xs text-gray-400 mt-1">You can also edit the transcript manually</p>
        </div>

        <button onClick={handleSave} disabled={saving || !transcript.trim()} className="btn-primary w-full justify-center">
          {saving ? <span className="spinner" /> : <Send className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save as Symptoms'}
        </button>
      </div>

      <DisclaimerBox text="Voice recognition may not be 100% accurate. Please review the transcript before saving. This does not provide medical diagnosis." />
    </div>
  );
}
