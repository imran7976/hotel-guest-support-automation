'use client';

import React, { useState } from 'react';
import { Header } from '@/components/Header';
import {
  Hotel,
  Bot,
  ShieldCheck,
  Bell,
  Link2,
  CheckCircle2,
  Save,
  Server
} from 'lucide-react';

export default function SettingsPage() {
  const [hotelName, setHotelName] = useState('Grand Azure Resort & Hotel');
  const [frontDeskPhone, setFrontDeskPhone] = useState('+1-555-0199');
  const [supportEmail, setSupportEmail] = useState('support@grandhotelazure.demo');
  const [aiModel, setAiModel] = useState('gpt-4o-mini');
  const [confidenceThreshold, setConfidenceThreshold] = useState('0.75');
  const [temperature, setTemperature] = useState('0.2');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header
        title="System & Automation Settings"
        subtitle="Manage hotel profile, AI confidence thresholds, n8n webhook parameters, and integration health."
      />

      <div className="flex-1 p-8 space-y-8 overflow-y-auto max-w-4xl">
        {saved && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            Configuration parameters saved successfully!
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Section 1: Hotel Profile */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
              <Hotel className="h-4 w-4 text-sky-600" />
              <h3 className="font-bold text-slate-900 text-sm">Hotel Property Profile</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Hotel Legal Name</label>
                <input
                  type="text"
                  value={hotelName}
                  onChange={(e) => setHotelName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Front Desk Phone</label>
                <input
                  type="text"
                  value={frontDeskPhone}
                  onChange={(e) => setFrontDeskPhone(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs font-mono"
                />
              </div>

              <div className="md:col-span-2">
                <label className="font-semibold text-slate-700 block mb-1">Support Dispatch Email</label>
                <input
                  type="email"
                  value={supportEmail}
                  onChange={(e) => setSupportEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs font-mono"
                />
              </div>
            </div>
          </div>

          {/* Section 2: AI Model & Triage Parameters */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
              <Bot className="h-4 w-4 text-indigo-600" />
              <h3 className="font-bold text-slate-900 text-sm">AI Agent & Reasoning Configuration</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Configured Model</label>
                <select
                  value={aiModel}
                  onChange={(e) => setAiModel(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white font-mono"
                >
                  <option value="gpt-4o-mini">gpt-4o-mini (Default)</option>
                  <option value="gpt-4o">gpt-4o</option>
                  <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                </select>
                <p className="text-[10px] text-slate-400 mt-1">Loaded via OPENAI_MODEL_NAME</p>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Confidence Escalation Cutoff
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.5"
                  max="0.99"
                  value={confidenceThreshold}
                  onChange={(e) => setConfidenceThreshold(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs font-mono"
                />
                <p className="text-[10px] text-slate-400 mt-1">Inquiries below this escalate to human</p>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Sampling Temperature</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.0"
                  max="1.0"
                  value={temperature}
                  onChange={(e) => setTemperature(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs font-mono"
                />
                <p className="text-[10px] text-slate-400 mt-1">0.2 provides high grounding consistency</p>
              </div>
            </div>
          </div>

          {/* Section 3: Integration Health & Security */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
              <Server className="h-4 w-4 text-emerald-600" />
              <h3 className="font-bold text-slate-900 text-sm">Integration Status & Safe Guardrails</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-slate-800">FastAPI Backend</p>
                  <p className="text-[11px] text-slate-400">REST API Gateway & Pydantic Schema Validation</p>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  CONNECTED
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-slate-800">MySQL 8.0+ Database</p>
                  <p className="text-[11px] text-slate-400">InnoDB UTF-8 Unicode, FULLTEXT Indexing</p>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  CONNECTED
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-slate-800">n8n Workflow Engine</p>
                  <p className="text-[11px] text-slate-400">5 Automated Workflows Exported to backend/n8n/workflows/</p>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  ENABLED
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-slate-800">Mock Notification Mode</p>
                  <p className="text-[11px] text-slate-400">Guarantees safe sandbox operation without sending real emails</p>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800">
                  DEMO ACTIVE
                </span>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              className="flex items-center gap-1.5 px-6 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs shadow-md shadow-sky-600/20 transition-all"
            >
              <Save className="h-4 w-4" />
              Save Configuration
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

