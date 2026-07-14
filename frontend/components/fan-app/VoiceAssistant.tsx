"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { Language } from "@/types";
import { Mic, MicOff, Loader2 } from "lucide-react";

export default function VoiceAssistant({ language }: { language: Language }) {
  const [connecting, setConnecting] = useState(false);
  const [active, setActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fanId = useState(() => crypto.randomUUID())[0];

  const startVoiceSession = async () => {
    setConnecting(true);
    setError(null);
    try {
      await apiClient.createVoiceSession({ fan_id: fanId, language });
      // Actual LiveKit room connection happens via @livekit/components-react
      // in a dedicated voice call view — this establishes the session token.
      setActive(true);
    } catch (err) {
      console.error("Voice session creation failed:", err);
      setError("Couldn't start voice session. Please try again.");
    } finally {
      setConnecting(false);
    }
  };

  const endVoiceSession = () => {
    setActive(false);
  };

  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
      <h2 className="text-stadium-text font-semibold mb-3 text-lg">Voice Assistant</h2>
      <p className="text-stadium-muted text-xs mb-4">
        Speak naturally — ask for directions, tickets, or anything else.
      </p>

      {error && <p className="text-stadium-critical text-sm mb-3">{error}</p>}

      <button
        onClick={active ? endVoiceSession : startVoiceSession}
        disabled={connecting}
        aria-pressed={active}
        className={`w-full flex items-center justify-center gap-2 rounded-lg py-3 text-sm font-medium transition-colors ${
          active
            ? "bg-stadium-critical/20 text-stadium-critical border border-stadium-critical"
            : "bg-stadium-accent text-stadium-dark"
        }`}
      >
        {connecting ? (
          <Loader2 size={18} className="animate-spin" />
        ) : active ? (
          <>
            <MicOff size={18} /> End Conversation
          </>
        ) : (
          <>
            <Mic size={18} /> Start Voice Chat
          </>
        )}
      </button>
    </div>
  );
}