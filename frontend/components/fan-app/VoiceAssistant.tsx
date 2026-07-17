"use client";
import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { Language } from "@/types";
import { Mic, Loader2 } from "lucide-react";
import VoiceCallView from "./VoiceCallView";

export default function VoiceAssistant({ language }: { language: Language }) {
  const [connecting, setConnecting] = useState(false);
  const [session, setSession] = useState<{ livekitUrl: string; token: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fanId = useState(() => crypto.randomUUID())[0];

  const startVoiceSession = async () => {
    setConnecting(true);
    setError(null);
    try {
      const res = await apiClient.createVoiceSession({ fan_id: fanId, language });
      setSession({ livekitUrl: res.livekit_url, token: res.livekit_token });
    } catch (err) {
      console.error("Voice session creation failed:", err);
      setError("Couldn't start voice session. Please try again.");
    } finally {
      setConnecting(false);
    }
  };

  const endVoiceSession = () => {
    setSession(null);
  };

  if (session) {
    return (
      <VoiceCallView
        livekitUrl={session.livekitUrl}
        token={session.token}
        onDisconnect={endVoiceSession}
      />
    );
  }

  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
      <h2 className="text-stadium-text font-semibold mb-3 text-lg">Voice Assistant</h2>
      <p className="text-stadium-muted text-xs mb-4">
        Speak naturally — ask for directions, tickets, or anything else.
      </p>
      {error && <p className="text-stadium-critical text-sm mb-3">{error}</p>}
      <button
        onClick={startVoiceSession}
        disabled={connecting}
        className="w-full flex items-center justify-center gap-2 rounded-lg py-3 text-sm font-medium bg-stadium-accent text-stadium-dark transition-colors"
      >
        {connecting ? <Loader2 size={18} className="animate-spin" /> : <><Mic size={18} /> Start Voice Chat</>}
      </button>
    </div>
  );
}