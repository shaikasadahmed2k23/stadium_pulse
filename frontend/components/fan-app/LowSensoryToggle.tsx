"use client";

import { Volume2, VolumeX } from "lucide-react";

export default function LowSensoryToggle({
  enabled,
  onChange,
}: {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
}) {
  return (
    <button
      onClick={() => onChange(!enabled)}
      aria-pressed={enabled}
      aria-label="Toggle low-sensory routing mode"
      className={`flex items-center gap-2 text-sm rounded-lg px-3 py-2 border transition-colors ${
        enabled
          ? "bg-stadium-accent/20 border-stadium-accent text-stadium-accent"
          : "bg-stadium-card border-white/10 text-stadium-muted"
      }`}
    >
      {enabled ? <VolumeX size={16} /> : <Volume2 size={16} />}
      Low-sensory mode
    </button>
  );
}