'use client';

import React, { useEffect, useState } from 'react';
import { Header } from '@/components/Header';
import { api, KnowledgeItem } from '@/lib/api';
import {
  BookOpenCheck,
  Search,
  Plus,
  Edit,
  Trash2,
  RefreshCw,
  Tag,
  CheckCircle,
  X,
  FileText
} from 'lucide-react';

export default function KnowledgeBasePage() {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<KnowledgeItem | null>(null);

  // Form states
  const [formCategory, setFormCategory] = useState('check_in_out');
  const [formTitle, setFormTitle] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formKeywords, setFormKeywords] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadKnowledge = async () => {
    try {
      setLoading(true);
      const data = await api.getKnowledge(selectedCategory);
      setItems(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledge();
  }, [selectedCategory]);

  const handleOpenCreate = () => {
    setEditingItem(null);
    setFormCategory('check_in_out');
    setFormTitle('');
    setFormContent('');
    setFormKeywords('');
    setIsModalOpen(true);
  };

  const handleOpenEdit = (item: KnowledgeItem) => {
    setEditingItem(item);
    setFormCategory(item.category);
    setFormTitle(item.title);
    setFormContent(item.content);
    setFormKeywords(item.keywords || '');
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this hotel knowledge article?')) return;
    try {
      await api.deleteKnowledge(id);
      loadKnowledge();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      if (editingItem) {
        await api.updateKnowledge(editingItem.id, {
          category: formCategory,
          title: formTitle,
          content: formContent,
          keywords: formKeywords,
        });
      } else {
        await api.createKnowledge({
          category: formCategory,
          title: formTitle,
          content: formContent,
          keywords: formKeywords,
        });
      }
      setIsModalOpen(false);
      loadKnowledge();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredItems = items.filter(
    (i) =>
      i.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      i.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (i.keywords && i.keywords.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const categories = [
    'all',
    'check_in_out',
    'facilities',
    'dining',
    'wifi',
    'cancellation',
    'policies',
    'contact',
    'faq',
  ];

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header
        title="Hotel Knowledge Base (RAG)"
        subtitle="Manage verified policies, FAQs, and property details queried by the AI reasoning engine."
        action={
          <button
            onClick={handleOpenCreate}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs shadow-xs transition-all"
          >
            <Plus className="h-3.5 w-3.5" />
            Add Knowledge Article
          </button>
        }
      />

      <div className="flex-1 p-8 space-y-6 overflow-y-auto">
        {/* Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200">
          <div className="relative w-full sm:w-80">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search knowledge title or policy..."
              className="w-full pl-9 pr-3 py-2 bg-slate-50 rounded-lg border border-slate-200 text-xs focus:ring-2 focus:ring-sky-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-500 uppercase mr-1">Category:</span>
            {categories.map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCategory(c)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium capitalize transition-all ${
                  selectedCategory === c
                    ? 'bg-sky-600 text-white shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {c.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Knowledge Articles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {loading ? (
            <div className="col-span-full py-12 text-center text-xs text-slate-400">
              Loading knowledge repository...
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="col-span-full py-12 text-center text-xs text-slate-400">
              No knowledge entries found in this category.
            </div>
          ) : (
            filteredItems.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-all"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-sky-50 text-sky-700 border border-sky-100">
                      {item.category.replace(/_/g, ' ')}
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleOpenEdit(item)}
                        className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                      >
                        <Edit className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="p-1 rounded text-slate-400 hover:text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>

                  <h4 className="font-bold text-slate-900 text-sm leading-snug">{item.title}</h4>

                  <p className="text-xs text-slate-600 leading-relaxed line-clamp-4">
                    {item.content}
                  </p>

                  {item.keywords && (
                    <div className="flex items-center gap-1.5 pt-2 text-[10px] text-slate-400">
                      <Tag className="h-3 w-3" />
                      <span className="truncate">{item.keywords}</span>
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                  <span className="flex items-center gap-1 text-emerald-600 font-medium">
                    <CheckCircle className="h-3 w-3" /> Grounded in RAG
                  </span>
                  <span>ID #{item.id}</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Modal for Create/Edit */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-slate-900 text-sm">
                  {editingItem ? 'Edit Knowledge Article' : 'Create Knowledge Article'}
                </h3>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-3 text-xs">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Category</label>
                  <select
                    value={formCategory}
                    onChange={(e) => setFormCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs capitalize bg-white"
                  >
                    {categories
                      .filter((c) => c !== 'all')
                      .map((c) => (
                        <option key={c} value={c}>
                          {c.replace(/_/g, ' ')}
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Article Title</label>
                  <input
                    type="text"
                    required
                    value={formTitle}
                    onChange={(e) => setFormTitle(e.target.value)}
                    placeholder="e.g. Infinity Pool Operational Hours & Towels"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">
                    Grounded Content (Queried by AI)
                  </label>
                  <textarea
                    rows={5}
                    required
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                    placeholder="Provide factual, explicit hotel policy or information..."
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Keywords (Comma-separated)</label>
                  <input
                    type="text"
                    value={formKeywords}
                    onChange={(e) => setFormKeywords(e.target.value)}
                    placeholder="pool, swimming, hours, towels, cabana"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  />
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-3 py-2 rounded-lg border border-slate-200 text-slate-600 font-medium text-xs"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs shadow-xs disabled:opacity-50"
                  >
                    {submitting ? 'Saving...' : editingItem ? 'Update Article' : 'Publish Article'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

