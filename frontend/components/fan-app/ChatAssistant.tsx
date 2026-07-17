"use client";

import { useState, useRef, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import type { Language } from "@/types";
import { Send, MessageCircle } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export default function ChatAssistant({ language }: { language: Language }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Welcome to FIFA World Cup 2026! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const sessionId = useRef(crypto.randomUUID());
  const scrollRef = useRef<HTMLDivElement>(null);

useEffect(() => {
    if (scrollRef.current && typeof scrollRef.current.scrollTo === "function") {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const response = await apiClient.sendChatMessage({
        message: trimmed,
        language,
        session_id: sessionId.current,
      });
      setMessages((prev) => [...prev, { role: "assistant", text: response.reply }]);
    } catch (err) {
      console.error("Chat message failed:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-white/5 flex flex-col h-[420px]">
      <h2 className="text-stadium-text font-semibold mb-3 text-lg flex items-center gap-2">
        <MessageCircle size={20} className="text-stadium-accent" />
        Fan Assistant
      </h2>

      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-2 mb-3 pr-1">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`text-sm rounded-lg px-3 py-2 max-w-[85%] ${
              msg.role === "user"
                ? "bg-stadium-accent/20 text-stadium-text ml-auto"
                : "bg-stadium-dark text-stadium-text"
            }`}
          >
            {msg.text}
          </div>
        ))}
        {loading && (
          <div className="bg-stadium-dark text-stadium-muted text-sm rounded-lg px-3 py-2 max-w-[85%]">
            Typing…
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask about tickets, food, restrooms…"
          aria-label="Chat message"
          className="flex-1 bg-stadium-dark border border-white/10 text-stadium-text text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-stadium-accent"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          aria-label="Send message"
          className="bg-stadium-accent text-stadium-dark rounded-lg px-3 py-2 disabled:opacity-50"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}