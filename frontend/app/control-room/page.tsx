"use client";

import { useControlRoomSocket } from "@/hooks/useWebSocket";
import ZoneHeatmap from "@/components/control-room/ZoneHeatmap";
import ReasoningTrace from "@/components/control-room/ReasoningTrace";
import IncidentAlert from "@/components/control-room/IncidentAlert";
import DecisionFeed from "@/components/control-room/DecisionFeed";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

export default function ControlRoomPage() {
  const { state, connected } = useControlRoomSocket();

  return (
    <main className="min-h-screen bg-stadium-dark p-6 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-stadium-text">
              StadiumPulse Control Room
            </h1>
            <p className="text-stadium-muted text-sm mt-1">
              FIFA World Cup 2026 — Live Operations Dashboard
            </p>
          </div>
          <DecisionFeed connected={connected} />
        </div>

        {!state ? (
          <div className="flex justify-center py-20">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="space-y-6">
            <ZoneHeatmap zones={state.zones} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <IncidentAlert incidents={state.active_incidents} />
              <ReasoningTrace recommendations={state.active_recommendations} />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}