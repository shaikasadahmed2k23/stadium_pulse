"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { Language, NavigationResponse } from "@/types";
import { Navigation, Loader2 } from "lucide-react";

export default function NavigationMap({
  language,
  lowSensoryMode,
}: {
  language: Language;
  lowSensoryMode: boolean;
}) {
  const [query, setQuery] = useState("");
  const [currentZone, setCurrentZone] = useState("gate_1");
  const [result, setResult] = useState<NavigationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getNavigationRoute({
        query,
        current_zone: currentZone,
        language,
        low_sensory_mode: lowSensoryMode,
      });
      setResult(response);
    } catch (err) {
      console.error("Navigation lookup failed:", err);
      setError("Couldn't find a route — try rephrasing your request.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-stadium-card rounded-xl p-5 border border-white/5">
      <h2 className="text-stadium-text font-semibold mb-4 text-lg flex items-center gap-2">
        <Navigation size={20} className="text-stadium-accent" />
        Find Your Way
      </h2>

      <div className="flex gap-2 mb-4">
        <select
          value={currentZone}
          onChange={(e) => setCurrentZone(e.target.value)}
          aria-label="Your current location"
          className="bg-stadium-dark border border-white/10 text-stadium-text text-sm rounded-lg px-2 py-2 focus:outline-none focus:ring-2 focus:ring-stadium-accent"
        >
          <option value="gate_1">Gate 1</option>
          <option value="gate_2">Gate 2</option>
          <option value="gate_3">Gate 3</option>
          <option value="concourse_a">Concourse A</option>
          <option value="concourse_b">Concourse B</option>
          <option value="section_101">Section 101</option>
        </select>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Where do you want to go?"
          aria-label="Navigation query"
          className="flex-1 bg-stadium-dark border border-white/10 text-stadium-text text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-stadium-accent"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-stadium-accent text-stadium-dark font-medium text-sm rounded-lg px-4 py-2 disabled:opacity-50"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : "Go"}
        </button>
      </div>

      {error && <p className="text-stadium-critical text-sm mb-3">{error}</p>}

      {result && (
        <div className="space-y-2">
          <p className="text-stadium-muted text-xs mb-2">
            Estimated time: {Math.round(result.total_estimated_time_seconds / 60)} min
            {result.route_avoids_congestion && " · Avoiding congestion"}
          </p>
          {result.route.map((step, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 text-sm text-stadium-text bg-stadium-dark rounded-lg p-2.5"
            >
              <span className="w-5 h-5 rounded-full bg-stadium-accent/20 text-stadium-accent flex items-center justify-center text-xs font-bold shrink-0">
                {idx + 1}
              </span>
              <span>{step.instruction}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}