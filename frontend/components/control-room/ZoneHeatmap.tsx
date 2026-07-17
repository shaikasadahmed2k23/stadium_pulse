"use client";

import { memo } from "react";
import type { ZoneData } from "@/types";

const statusColors: Record<string, string> = {
  normal: "bg-stadium-accent/20 border-stadium-accent text-stadium-accent",
  elevated: "bg-stadium-warning/20 border-stadium-warning text-stadium-warning",
  critical: "bg-stadium-critical/20 border-stadium-critical text-stadium-critical animate-pulse",
};

function ZoneHeatmap({ zones }: { zones: ZoneData[] }) {
  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
      <h2 className="text-stadium-text font-semibold mb-4 text-lg">Zone Occupancy</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {zones.map((zone) => (
          <div
            key={zone.zone_id}
            className={`rounded-lg border p-4 transition-colors ${statusColors[zone.status]}`}
          >
            <p className="text-sm font-medium text-stadium-text">{zone.zone_name}</p>
            <p className="text-2xl font-bold mt-1">{zone.occupancy_percentage}%</p>
            <p className="text-xs text-stadium-muted mt-1">
              {zone.current_occupancy.toLocaleString()} / {zone.max_capacity.toLocaleString()}
            </p>
            {zone.predicted_occupancy_10min !== null && (
              <p className="text-xs mt-2 text-stadium-muted">
                Predicted (10min): {zone.predicted_occupancy_10min.toLocaleString()}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default memo(ZoneHeatmap);