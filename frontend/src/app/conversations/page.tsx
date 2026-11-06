'use client';

import React, { useEffect, useState } from 'react';
import { Header } from '@/components/Header';
import { api, ConversationSummary, ConversationDetail } from '@/lib/api';
import {
  Search,
  Filter,
  MessageSquare,
  Bot,
  User,
  ShieldAlert,
  Send,
  Calendar,
  X,
  RefreshCw
} from 'lucide-react';

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedConvId, setSelectedConvId] = useState<string | null>(null);
  const [convDetail, setConvDetail] = useState<ConversationDetail | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [sendingReply, setSendingReply] = useState(false);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await api.getConversations(statusFilter);
      setConversations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [statusFilter]);

  const openConversation = async (id: string) => {
    try {
      setSelectedConvId(id);
      setDetailLoading(true);
      const detail = await api.getConversation(id);
      setConvDetail(detail);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyText.trim() || !selectedConvId) return;
    try {
      setSendingReply(true);
      const newMsg = await api.postMessage(selectedConvId, replyText, 'staff');
      if (convDetail) {
        setConvDetail({
          ...convDetail,
          messages: [...convDetail.messages, newMsg],
        });
      }
      setReplyText('');
    } catch (err) {
      console.error(err);
    } finally {
      setSendingReply(false);
    }
  };

  const filteredConversations = conversations.filter(
    (c) =>
      c.guest_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.guest_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header
        title="Guest Conversations"
        subtitle="Review, audit, and intervene in live AI-managed hotel guest conversations."
        action={
          <button
            onClick={loadConversations}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        }
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Conversations List Panel */}
        <div className={`w-full ${selectedConvId ? 'lg:w-2/5' : 'w-full'} border-r border-slate-200 flex flex-col bg-white overflow-hidden transition-all duration-300`}>
          {/* Controls Header */}
          <div className="p-4 border-b border-slate-200 space-y-3 bg-slate-50/50">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search guest name, email, or ID..."
                className="w-full pl-9 pr-3 py-2 bg-white rounded-lg border border-slate-200 text-xs focus:outline-hidden focus:ring-2 focus:ring-sky-500"
              />
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Status:</span>
              {['all', 'active', 'escalated', 'closed'].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium capitalize transition-all ${
                    statusFilter === st
                      ? 'bg-sky-600 text-white shadow-xs'
                      : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>

          {/* List items */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading conversations...</div>
            ) : filteredConversations.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No conversations match your filter.</div>
            ) : (
              filteredConversations.map((c) => (
                <div
                  key={c.id}
                  onClick={() => openConversation(c.id)}
                  className={`p-4 cursor-pointer hover:bg-slate-50 transition-all ${
                    selectedConvId === c.id ? 'bg-sky-50/60 border-l-4 border-sky-600' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">{c.guest_name}</h4>
                      <p className="text-[11px] text-slate-400">{c.guest_email}</p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        c.status === 'escalated'
                          ? 'bg-red-100 text-red-700'
                          : c.status === 'active'
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>

                  <p className="mt-2 text-xs text-slate-600 line-clamp-2">
                    {c.last_message || 'No messages recorded.'}
                  </p>

                  <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-[10px]">
                      {c.id}
                    </span>
                    {c.last_intent && (
                      <span className="text-sky-600 font-medium capitalize">
                        {c.last_intent.replace(/_/g, ' ')}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Conversation Thread Detail Pane */}
        {selectedConvId && (
          <div className="flex-1 flex flex-col bg-slate-50/40 h-full overflow-hidden border-l border-slate-200">
            {detailLoading ? (
              <div className="flex-1 flex items-center justify-center text-xs text-slate-400">
                Loading thread details...
              </div>
            ) : convDetail ? (
              <>
                {/* Detail Header */}
                <div className="p-4 bg-white border-b border-slate-200 flex items-center justify-between shadow-xs">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-sm text-slate-900">
                        Conversation Thread: <span className="font-mono">{convDetail.id}</span>
                      </h3>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          convDetail.status === 'escalated'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-emerald-100 text-emerald-700'
                        }`}
                      >
                        {convDetail.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Channel: <span className="font-medium text-slate-700">{convDetail.channel}</span> | Messages: {convDetail.messages.length}
                    </p>
                  </div>

                  <button
                    onClick={() => setSelectedConvId(null)}
                    className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>

                {/* Messages Stream */}
                <div className="flex-1 p-6 overflow-y-auto space-y-4">
                  {convDetail.messages.map((m) => {
                    const isGuest = m.sender_type === 'guest';
                    const isAi = m.sender_type === 'ai';
                    const isStaff = m.sender_type === 'staff';

                    return (
                      <div
                        key={m.id}
                        className={`flex gap-3 max-w-2xl ${
                          isGuest ? 'mr-auto' : 'ml-auto flex-row-reverse'
                        }`}
                      >
                        <div
                          className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 text-white font-bold text-xs shadow-xs ${
                            isGuest
                              ? 'bg-slate-700'
                              : isAi
                              ? 'bg-gradient-to-tr from-sky-500 to-indigo-600'
                              : 'bg-emerald-600'
                          }`}
                        >
                          {isGuest ? <User className="h-4 w-4" /> : isAi ? <Bot className="h-4 w-4" /> : 'FO'}
                        </div>

                        <div className="space-y-1">
                          <div
                            className={`flex items-center gap-2 text-[11px] ${
                              isGuest ? 'justify-start' : 'justify-end'
                            }`}
                          >
                            <span className="font-bold text-slate-700">
                              {isGuest ? 'Guest' : isAi ? 'AI Concierge' : 'Front Desk Staff'}
                            </span>
                            <span className="text-slate-400">
                              {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                            {m.requires_human && (
                              <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-100 text-amber-700">
                                Escalated
                              </span>
                            )}
                          </div>

                          <div
                            className={`p-3.5 rounded-2xl text-xs leading-relaxed shadow-xs ${
                              isGuest
                                ? 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                                : isAi
                                ? 'bg-sky-600 text-white rounded-tr-none'
                                : 'bg-emerald-600 text-white rounded-tr-none'
                            }`}
                          >
                            {m.content}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Staff Reply Bar */}
                <form onSubmit={handleSendReply} className="p-4 bg-white border-t border-slate-200 flex gap-2">
                  <input
                    type="text"
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Intervene as Staff / Duty Manager..."
                    className="flex-1 px-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-sky-500"
                  />
                  <button
                    type="submit"
                    disabled={sendingReply || !replyText.trim()}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-lg flex items-center gap-1.5 shadow-xs disabled:opacity-50"
                  >
                    <Send className="h-3.5 w-3.5" />
                    Send Reply
                  </button>
                </form>
              </>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

