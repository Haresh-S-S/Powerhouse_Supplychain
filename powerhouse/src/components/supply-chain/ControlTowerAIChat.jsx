import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  RotateCw,
  HelpCircle,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';
import Button from '../ui/Button';
import apiClient from '../../services/apiClient';

const PROMPT_SUGGESTIONS = [
  'Why is TSMC Fab 14 at critical risk?',
  'What happens if Port of Kaohsiung closes for 10 days?',
  'Which warehouse is projected to run out of stock first?',
  'What is the safest alternative route for DRAM cargo?',
  'What rebalancing actions require executive approval?',
];

export default function ControlTowerAIChat({ businessId }) {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "Hello! I am your Supply Chain Control Tower AI Assistant, powered by Qwen3 and smolagents. I monitor live vendor risks, maritime disruption alerts, and multi-echelon inventory positions. How can I assist your operational decisions today?",
      citations: ['Live SupplyMind Feed', 'DistilBERT Risk Classifier', 'Inventory Fusion'],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (queryText) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || !businessId || sending) return;

    const userMsg = { sender: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setSending(true);

    try {
      const res = await apiClient.towerAgentChat({
        business_id: businessId,
        query: textToSend,
      });

      const assistantMsg = {
        sender: 'assistant',
        text: res.answer || "I have analyzed your query across active supply chain telemetry.",
        citations: res.citations || [],
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: "I encountered a communication issue while querying the local AI reasoning service. Please verify your connection or try again.",
          citations: [],
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 flex flex-col h-[540px]">
      {/* Header */}
      <div className="border-b border-[#1E293B] pb-3 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-indigo-950/70 border border-indigo-800 flex items-center justify-center text-indigo-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Supply Chain AI Assistant
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 font-mono">
                Qwen3 + smolagents
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Interactive natural language query interface grounded on real telemetry
            </p>
          </div>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4 scrollbar-thin">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.sender === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-indigo-950 border border-indigo-800 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed space-y-2 ${
                m.sender === 'user'
                  ? 'bg-indigo-600 text-white rounded-tr-none'
                  : 'bg-[#0B1120] text-slate-200 border border-slate-800 rounded-tl-none'
              }`}
            >
              <div className="whitespace-pre-line">{m.text}</div>

              {m.citations && m.citations.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-1.5 text-[10px] text-slate-400">
                  <span className="font-semibold text-slate-500">Grounded On:</span>
                  {m.citations.map((c, i) => (
                    <span key={i} className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-300 font-mono">
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {m.sender === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))}
        {sending && (
          <div className="flex items-center gap-2 text-xs text-indigo-400 p-2 bg-[#0B1120] rounded-xl w-fit border border-slate-800">
            <RotateCw className="w-3.5 h-3.5 animate-spin" />
            <span>Consulting smolagents & local Qwen3 model...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompts */}
      <div className="py-2 flex items-center gap-1.5 overflow-x-auto scrollbar-none border-t border-slate-800/60">
        {PROMPT_SUGGESTIONS.map((p, i) => (
          <button
            key={i}
            onClick={() => handleSend(p)}
            className="px-2.5 py-1 rounded-lg text-[10px] bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 whitespace-nowrap cursor-pointer transition-colors"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="pt-2 flex items-center gap-2"
      >
        <input
          type="text"
          placeholder="Ask anything about suppliers, port delays, stockouts, or rerouting..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          className="flex-1 bg-slate-900 text-xs text-slate-200 px-3.5 py-2.5 rounded-xl border border-slate-700 focus:outline-none focus:border-indigo-500"
        />
        <Button
          variant="primary"
          size="sm"
          type="submit"
          disabled={!inputQuery.trim() || sending}
          className="bg-indigo-600 hover:bg-indigo-500 text-white shrink-0 py-2.5 px-3.5"
        >
          <Send className="w-3.5 h-3.5" />
        </Button>
      </form>
    </div>
  );
}
