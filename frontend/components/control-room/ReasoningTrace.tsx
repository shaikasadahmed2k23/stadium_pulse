"use client";

import { memo, useState } from "react";
import type { DecisionRecommendation } from "@/types";
import { ChevronDown, ChevronUp } from "lucide-react";

const priorityColors: Record<string, string> = {
  low: "text-stadium-muted",
  medium: "text-stadium-warning",
  high: "text-stadium-warning",
  critical: "text-stadium-critical",
};

function ReasoningTrace({
  recommendations,
}: {
  recommendations: DecisionRecommendation[];
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (recommendations.length === 0) {
    return (
      <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
        <h2 className="text-stadium-text font-semibold mb-2 text-lg">Agent Recommendations</h2>
        <p className="text-stadium-muted text-sm">No active recommendations — all zones nominal.</p>
      </div>
    );
  }

  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
      <h2 className="text-stadium-text font-semibold mb-4 text-lg">Agent Recommendations</h2>
      <div className="space-y-3">
        {recommendations.map((rec) => {
          const isExpanded = expandedId === rec.recommendation_id;
          return (
            <div
              key={rec.recommendation_id}
              className="border border-white/10 rounded-lg p-3 cursor-pointer"
              onClick={() =>
                setExpandedId(isExpanded ? null : rec.recommendation_id)
              }
            >
              <div className="flex justify-between items-start gap-2">
                <div>
                  <p className="text-stadium-text text-sm font-medium">{rec.action}</p>
                  <p className={`text-xs mt-1 uppercase font-semibold ${priorityColors[rec.priority]}`}>
                    {rec.priority} · {Math.round(rec.confidence_score * 100)}% confidence
                  </p>
                </div>
                {isExpanded ? (
                  <ChevronUp size={18} className="text-stadium-muted shrink-0" />
                ) : (
                  <ChevronDown size={18} className="text-stadium-muted shrink-0" />
                )}
              </div>

              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-white/10 space-y-1.5">
                  <p className="text-xs text-stadium-muted font-medium mb-1">Why this recommendation:</p>
                  {rec.reasoning_factors.map((factor, idx) => (
                    <div key={idx} className="flex justify-between text-xs">
                      <span className="text-stadium-muted">{factor.factor.replace(/_/g, " ")}</span>
                      <span className="text-stadium-text font-medium">{factor.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default memo(ReasoningTrace);