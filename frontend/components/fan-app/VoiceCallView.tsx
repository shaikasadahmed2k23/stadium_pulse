"use client";
import { useEffect, useState, useCallback } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useRoomContext,
  useLocalParticipant,
  BarVisualizer,
  useVoiceAssistant,
} from "@livekit/components-react";
import { RoomEvent, TranscriptionSegment, Participant } from "livekit-client";
import { Mic, MicOff, PhoneOff } from "lucide-react";

interface VoiceCallViewProps {
  livekitUrl: string;
  token: string;
  onDisconnect: () => void;
}

interface TranscriptLine {
  id: string;
  speaker: "fan" | "agent";
  text: string;
  final: boolean;
}

function CallUI({ onDisconnect }: { onDisconnect: () => void }) {
  const room = useRoomContext();
  const { localParticipant } = useLocalParticipant();
  const { state: agentState, audioTrack } = useVoiceAssistant();
  const [muted, setMuted] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);

  useEffect(() => {
    localParticipant.setMicrophoneEnabled(true).catch((err) => {
      console.error("Mic enable failed:", err);
    });
  }, [localParticipant]);

  useEffect(() => {
    const handleTranscription = (
      segments: TranscriptionSegment[],
      participant?: Participant
    ) => {
      setTranscript((prev) => {
        const isAgent = participant?.isAgent ?? participant?.identity?.includes("agent");
        const next = [...prev];
        for (const seg of segments) {
          const idx = next.findIndex((l) => l.id === seg.id);
          const line: TranscriptLine = {
            id: seg.id,
            speaker: isAgent ? "agent" : "fan",
            text: seg.text,
            final: seg.final,
          };
          if (idx >= 0) next[idx] = line;
          else next.push(line);
        }
        return next;
      });
    };
    room.on(RoomEvent.TranscriptionReceived, handleTranscription);
    return () => {
      room.off(RoomEvent.TranscriptionReceived, handleTranscription);
    };
  }, [room]);

  const toggleMic = useCallback(async () => {
    const next = !muted;
    await localParticipant.setMicrophoneEnabled(!next);
    setMuted(next);
  }, [muted, localParticipant]);

  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
      <h2 className="text-stadium-text font-semibold mb-1 text-lg">Voice Assistant</h2>
      <p className="text-stadium-muted text-xs mb-4">
        Status: {agentState ?? "connecting..."}
      </p>

      <div className="h-16 mb-4 flex items-center justify-center">
        {audioTrack ? (
          <BarVisualizer state={agentState} trackRef={audioTrack} barCount={5} />
        ) : (
          <p className="text-stadium-muted text-xs">Waiting for agent audio...</p>
        )}
      </div>

      <div className="max-h-48 overflow-y-auto mb-4 space-y-2 text-sm">
        {transcript.length === 0 && (
          <p className="text-stadium-muted text-xs">Transcript will appear here...</p>
        )}
        {transcript.map((line) => (
          <div
            key={line.id}
            className={line.speaker === "agent" ? "text-stadium-accent" : "text-stadium-text"}
          >
            <span className="font-medium">{line.speaker === "agent" ? "Assistant: " : "You: "}</span>
            {line.text}
            {!line.final && <span className="opacity-50">...</span>}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <button
          onClick={toggleMic}
          className="flex-1 flex items-center justify-center gap-2 rounded-lg py-3 text-sm font-medium bg-white/5 text-stadium-text border border-white/10"
        >
          {muted ? <MicOff size={18} /> : <Mic size={18} />}
          {muted ? "Unmute" : "Mute"}
        </button>
        <button
          onClick={onDisconnect}
          className="flex-1 flex items-center justify-center gap-2 rounded-lg py-3 text-sm font-medium bg-stadium-critical/20 text-stadium-critical border border-stadium-critical"
        >
          <PhoneOff size={18} /> End Call
        </button>
      </div>
    </div>
  );
}

export default function VoiceCallView({ livekitUrl, token, onDisconnect }: VoiceCallViewProps) {
  return (
    <LiveKitRoom
      serverUrl={livekitUrl}
      token={token}
      connect={true}
      audio={true}
      onDisconnected={onDisconnect}
      data-lk-theme="default"
    >
      <RoomAudioRenderer />
      <CallUI onDisconnect={onDisconnect} />
    </LiveKitRoom>
  );
}