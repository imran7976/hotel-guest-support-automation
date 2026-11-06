'use client';

import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { api } from '@/lib/api';
import {
  Send,
  Bot,
  User,
  Sparkles,
  ShieldAlert,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Zap
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'guest' | 'ai';
  text: string;
  intent?: string;
  confidence?: number;
  priority?: string;
  requires_human?: boolean;
  retrieved_knowledge?: string[];
  timestamp: string;
}

export default function AIChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: 'Hello! I am Grand Azure Resort\'s AI Concierge. How may I assist you with your stay, reservation, check-in, or hotel amenities today?',
      timestamp: 'Just now',
    },
  ]);
  const [input, setInput] = useState('');
  const [guestName, setGuestName] = useState('John Smith');
  const [guestEmail, setGuestEmail] = useState('john@example.com');
  const [bookingRef, setBookingRef] = useState('GAH-78901');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (textToSend: string) => {
    const trimmed = textToSend.trim();
    if (!trimmed || loading) return;

    setError(null);
    const guestMsg: ChatMessage = {
      id: `guest_${Date.now()}`,
      sender: 'guest',
      text: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, guestMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.processInquiry({
        guest_name: guestName,
        email: guestEmail,
        inquiry_message: trimmed,
        booking_reference: bookingRef || undefined,
        conversation_id: conversationId,
        channel: 'web_chat',
      });

      if (!conversationId) {
        setConversationId(res.conversation_id);
      }

      const aiMsg: ChatMessage = {
        id: `ai_${Date.now()}`,
        sender: 'ai',
        text: res.response,
        intent: res.intent,
        confidence: res.confidence,
        priority: res.priority,
        requires_human: res.requires_human,
        retrieved_knowledge: res.retrieved_knowledge,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setError(err.message || 'Error communicating with AI engine.');
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioClick = (scenarioText: string) => {
    setInput(scenarioText);
  };

  const requestHumanAssistance = () => {
    sendMessage('I would like to speak with a human front-desk representative, please.');
  };

  const resetChat = () => {
    setMessages([
      {
        id: 'welcome',
        sender: 'ai',
        text: 'Hello! I am Grand Azure Resort\'s AI Concierge. How may I assist you with your stay, reservation, check-in, or hotel amenities today?',
        timestamp: 'Just now',
      },
    ]);
    setConversationId(undefined);
    setError(null);
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header
        title="AI Support Chat & Live Sandbox"
        subtitle="Simulated guest experience demonstrating real-time RAG grounding, intent triage, and escalation."
        action={
          <button
            onClick={resetChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Reset Session
          </button>
        }
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Chat Conversation Area */}
        <div className="flex-1 flex flex-col bg-slate-50 overflow-hidden">
          {/* Messages Container */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {messages.map((m) => {
              const isGuest = m.sender === 'guest';
              return (
                <div
                  key={m.id}
                  className={`flex gap-3 max-w-2xl ${isGuest ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
                >
                  <div
                    className={`h-9 w-9 rounded-full flex items-center justify-center shrink-0 text-white font-bold text-xs shadow-xs ${
                      isGuest ? 'bg-slate-800' : 'bg-gradient-to-tr from-sky-500 to-indigo-600'
                    }`}
                  >
                    {isGuest ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>

                  <div className="space-y-1.5">
                    <div className={`flex items-center gap-2 text-[11px] ${isGuest ? 'justify-end' : 'justify-start'}`}>
                      <span className="font-bold text-slate-700">{isGuest ? guestName : 'Grand Azure AI'}</span>
                      <span className="text-slate-400">{m.timestamp}</span>
                    </div>

                    <div
                      className={`p-4 rounded-2xl text-xs leading-relaxed shadow-xs ${
                        isGuest
                          ? 'bg-sky-600 text-white rounded-tr-none'
                          : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                      }`}
                    >
                      {m.text}

                      {/* AI Metadata Tags */}
                      {!isGuest && m.intent && (
                        <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-2 text-[10px]">
                          <span className="px-2 py-0.5 rounded-md bg-sky-50 text-sky-700 font-mono font-medium">
                            Intent: {m.intent} ({Math.round((m.confidence || 0) * 100)}%)
                          </span>
                          {m.requires_human ? (
                            <span className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 font-bold flex items-center gap-1 border border-amber-200">
                              <ShieldAlert className="h-3 w-3 text-amber-600" />
                              Human Staff Escalated
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 font-medium flex items-center gap-1">
                              <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                              AI Resolved
                            </span>
                          )}
                          {m.retrieved_knowledge && m.retrieved_knowledge.length > 0 && (
                            <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                              RAG: {m.retrieved_knowledge.join(', ')}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="flex gap-3 mr-auto max-w-md">
                <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shrink-0">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="p-4 rounded-2xl rounded-tl-none bg-white border border-slate-200 text-slate-400 text-xs flex items-center gap-2 shadow-xs">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 rounded-full bg-sky-400 animate-bounce"></span>
                    <span className="h-2 w-2 rounded-full bg-sky-400 animate-bounce [animation-delay:0.2s]"></span>
                    <span className="h-2 w-2 rounded-full bg-sky-400 animate-bounce [animation-delay:0.4s]"></span>
                  </div>
                  <span>Retrieving hotel knowledge & reasoning...</span>
                </div>
              </div>
            )}
          </div>

          {/* Quick Scenario Buttons */}
          <div className="px-6 py-2 bg-slate-100/70 border-t border-slate-200 flex items-center gap-2 overflow-x-auto text-xs">
            <span className="text-[11px] font-semibold text-slate-500 shrink-0 flex items-center gap-1">
              <Zap className="h-3.5 w-3.5 text-amber-500" /> Test Scenarios:
            </span>
            <button
              onClick={() =>
                handleScenarioClick(
                  'Hello, I have a booking for tomorrow. Could you tell me the check-in time and whether I can request an early check-in?'
                )
              }
              className="px-2.5 py-1 rounded bg-white border border-slate-200 text-slate-700 hover:bg-sky-50 hover:border-sky-300 transition-all shrink-0"
            >
              1. Check-in & Policy
            </button>
            <button
              onClick={() =>
                handleScenarioClick(
                  "My room's air conditioning is not working, and I have already contacted reception twice."
                )
              }
              className="px-2.5 py-1 rounded bg-white border border-slate-200 text-slate-700 hover:bg-amber-50 hover:border-amber-300 transition-all shrink-0"
            >
              2. Urgent AC Complaint
            </button>
            <button
              onClick={() => handleScenarioClick('Please cancel my reservation and issue a refund.')}
              className="px-2.5 py-1 rounded bg-white border border-slate-200 text-slate-700 hover:bg-red-50 hover:border-red-300 transition-all shrink-0"
            >
              3. Cancellation & Refund
            </button>
            <button
              onClick={requestHumanAssistance}
              className="px-2.5 py-1 rounded bg-slate-200 text-slate-700 hover:bg-slate-300 transition-all shrink-0 font-medium"
            >
              Request Human Representative
            </button>
          </div>

          {/* Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
            className="p-4 bg-white border-t border-slate-200 flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about check-in, pool, Wi-Fi, or your reservation..."
              disabled={loading}
              className="flex-1 px-4 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-sky-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs rounded-xl flex items-center gap-1.5 shadow-md shadow-sky-600/20 disabled:opacity-50 transition-all"
            >
              <Send className="h-3.5 w-3.5" />
              Send
            </button>
          </form>
        </div>

        {/* Guest Session Sidebar Controls */}
        <div className="w-80 border-l border-slate-200 bg-white p-6 space-y-6 hidden lg:block overflow-y-auto">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Simulated Guest Context</h3>
            <p className="text-xs text-slate-500 mt-0.5">Parameters sent with each API payload</p>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Guest Full Name</label>
              <input
                type="text"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Guest Email</label>
              <input
                type="email"
                value={guestEmail}
                onChange={(e) => setGuestEmail(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Booking Reference</label>
              <input
                type="text"
                value={bookingRef}
                onChange={(e) => setBookingRef(e.target.value)}
                placeholder="e.g. GAH-78901"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs font-mono uppercase"
              />
            </div>

            {conversationId && (
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Session ID</span>
                <span className="font-mono text-xs text-sky-600 font-semibold">{conversationId}</span>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-200 text-xs text-slate-500 space-y-2">
            <h4 className="font-bold text-slate-700 text-[11px] uppercase tracking-wider">How This Works</h4>
            <p className="leading-relaxed">
              Inquiries pass through FastAPI, triggering intent classification across 12 categories.
              Grounding context is extracted from MySQL hotel policies via RAG. Responses strictly enforce
              human-in-the-loop policies for refunds, changes, and urgent complaints.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

