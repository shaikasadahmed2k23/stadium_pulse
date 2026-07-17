"use client";

import { Wifi, WifiOff } from "lucide-react";

export default function DecisionFeed({ connected }: { connected: boolean }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      {connected ? (
        <>
          <Wifi size={16} className="text-stadium-accent" />
          <span className="text-stadium-accent">Live feed connected</span>
        </>
      ) : (
        <>
          <WifiOff size={16} className="text-stadium-critical" />
          <span className="text-stadium-critical">Reconnecting…</span>
        </>
      )}
    </div>
  );
}