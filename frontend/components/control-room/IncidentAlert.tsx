"use client";

import { memo } from "react";
import type { IncidentAlert as IncidentAlertType } from "@/types";
import { AlertTriangle, Radio } from "lucide-react";

function IncidentAlert({ incidents }: { incidents: IncidentAlertType[] }) {
  if (incidents.length === 0) {
    return (
      <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
        <h2 className="text-stadium-text font-semibold mb-2 text-lg">Active Incidents</h2>
        <p className="text-stadium-muted text-sm">No active incidents. All clear.</p>
      </div>
    );
  }

  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-stadium-critical/30">
      <h2 className="text-stadium-text font-semibold mb-4 text-lg flex items-center gap-2">
        <AlertTriangle size={20} className="text-stadium-critical" />
        Active Incidents ({incidents.length})
      </h2>
      <div className="space-y-3">
        {incidents.map((incident) => (
          <div
            key={incident.incident_id}
            className="bg-stadium-critical/10 border border-stadium-critical/30 rounded-lg p-3"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-stadium-critical text-xs font-semibold uppercase">
                {incident.incident_type.replace(/_/g, " ")}
              </span>
              {incident.auto_detected && (
                <span className="flex items-center gap-1 text-xs text-stadium-muted">
                  <Radio size={12} /> Auto-detected
                </span>
              )}
            </div>
            <p className="text-stadium-text text-sm">{incident.description}</p>
            <p className="text-stadium-muted text-xs mt-2">
              <span className="font-medium">Suggested:</span> {incident.suggested_action}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default memo(IncidentAlert);