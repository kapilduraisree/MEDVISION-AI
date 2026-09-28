import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Volume2, Bot, User, AlertTriangle, Plus } from 'lucide-react';
import { chatbotAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-600'}`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-gray-600 dark:text-gray-300" />}
      </div>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${isUser ? 'bg-primary-600 text-white rounded-tr-none' : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-none shadow-sm border border-gray-100 dark:border-gray-600'}`}>
        {msg.is_emergency && (
          <div className="flex items-center gap-1.5 text-red-500 font-bold text-xs mb-2">
            <AlertTriangle className="w-3.5 h-3.5" /> EMERGENCY ALERT
          </div>
        )}
        <div className="text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown>{msg.message || msg.text}</ReactMarkdown>
        </div>
        <p className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
          {new Date(msg.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}

export default function ChatbotPage() {
  const { user } = useAuth();
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState('');
  const [language, setLanguage]   = useState(user?.preferred_language || 'en');
  const [sessionId, setSessionId] = useState(null);
  const [sending, setSending]     = useState(false);
  const [recording, setRecording] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    setMessages([{
      role: 'assistant',
      message: language === 'ta'
        ? 'வணக்கம்! நான் MedVision AI உதவியாளர். மருத்துவ சொற்கள், ஆய்வக முடிவுகள் அல்லது பொதுவான சுகாதார தகவல்களைப் பற்றி கேளுங்கள். ⚠️ நான் நோய்களை கண்டறிவதோ மருந்துகளை பரிந்துரைப்பதோ செய்யமாட்டேன்.'
        : 'Hello! I\'m the MedVision AI Assistant. Ask me about medical terms, lab results, or general health information. ⚠️ I do not diagnose conditions or prescribe medications.',
      created_at: new Date().toISOString(),
    }]);
  }, [language]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: 'user', message: text, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setSending(true);
    try {
      const res = await chatbotAPI.sendMessage({ message: text, language, session_id: sessionId });
      if (!sessionId) setSessionId(res.data.session_id);
      setMessages(prev => [...prev, {
        role: 'assistant',
        message: res.data.response,
        is_emergency: res.data.is_emergency,
        created_at: new Date().toISOString(),
      }]);
    } catch { toast.error('Failed to get response'); }
    finally { setSending(false); }
  };

  const startVoice = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice not supported in this browser'); return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const r  = new SR();
    r.lang = language === 'ta' ? 'ta-IN' : 'en-IN';
    r.onresult = (e) => { setInput(Array.from(e.results).map(x => x[0].transcript).join('')); };
    r.onerror  = () => setRecording(false);
    r.onend    = () => setRecording(false);
    r.start(); recognitionRef.current = r; setRecording(true);
  };

  const speakResponse = (text) => {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text.replace(/[#*⚠️🚨💡]/g, ''));
    u.lang = language === 'ta' ? 'ta-IN' : 'en-IN';
    window.speechSynthesis.speak(u);
  };

  const QUICK = language === 'ta'
    ? ['ஹீமோகுளோபின் என்றால் என்ன?', 'கொழுப்பு அதிகமாக இருந்தால்?', 'HbA1c என்பது என்ன?']
    : ['What is HbA1c?', 'What does high cholesterol mean?', 'Explain what hemoglobin is'];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl animate-fade-in">
      {/* Header */}
      <div className="card mb-4 flex items-center justify-between py-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-semibold text-gray-900 dark:text-white">MedVision AI Assistant</p>
            <p className="text-xs text-green-500 flex items-center gap-1"><span className="w-1.5 h-1.5 bg-green-500 rounded-full inline-block" />Online</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select className="input w-36 text-sm py-1.5" value={language} onChange={e => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="ta">தமிழ்</option>
          </select>
          <button onClick={() => { setMessages([]); setSessionId(null); }} className="btn-secondary py-1.5 text-xs">
            <Plus className="w-3.5 h-3.5" /> New Chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 px-1">
        {messages.map((m, i) => <Message key={i} msg={m} />)}
        {sending && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
              <Bot className="w-4 h-4 text-gray-600 dark:text-gray-300" />
            </div>
            <div className="bg-white dark:bg-gray-700 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm border border-gray-100 dark:border-gray-600">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => <div key={i} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />)}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick replies */}
      <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
        {QUICK.map(q => (
          <button key={q} onClick={() => sendMessage(q)} className="flex-shrink-0 text-xs px-3 py-1.5 rounded-full border border-primary-300 text-primary-700 dark:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors">
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="card py-3 flex items-center gap-2">
        <button onClick={recording ? () => recognitionRef.current?.stop() : startVoice}
          className={`p-2 rounded-lg transition-colors ${recording ? 'bg-red-100 text-red-600 animate-pulse' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500'}`}>
          <Mic className="w-5 h-5" />
        </button>
        <input
          className="flex-1 bg-transparent outline-none text-sm text-gray-800 dark:text-gray-200 placeholder-gray-400"
          placeholder={language === 'ta' ? 'உங்கள் கேள்வியை இங்கே தட்டச்சு செய்யுங்கள்...' : 'Type your health question here...'}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage(input))}
        />
        <button onClick={() => sendMessage(input)} disabled={sending || !input.trim()} className="p-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-40">
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
