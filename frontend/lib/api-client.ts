/**
 * Centralized API client for the FastAPI backend. Keeping all fetch
 * logic here means the components stay clean and we handle errors,
 * headers, and base URLs in exactly one place.
 */
import type {
  ControlRoomState,
  NavigationResponse,
  ChatResponse,
  VoiceSessionResponse,
  Language,
  IncidentType,
  Priority,
  ReasoningEntry,
  IncidentAlert,
  CrowdPredictionResponse,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const STAFF_API_KEY = process.env.NEXT_PUBLIC_STAFF_API_KEY || "";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  staffOnly = false
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (staffOnly) {
    headers["x-api-key"] = STAFF_API_KEY;
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new ApiError(response.status, errorBody || response.statusText);
  }

  return response.json();
}

export const apiClient = {
  // Control Room (staff-only)
  getControlRoomState: () =>
    request<ControlRoomState>("/api/control-room/state", {}, true),

  getReasoningTrace: (limit = 20) =>
    request<{ entries: ReasoningEntry[] }>(`/api/control-room/reasoning-trace?limit=${limit}`, {}, true),

  scanAnomalies: () =>
    request<IncidentAlert[]>("/api/control-room/scan-anomalies", { method: "POST" }, true),

  reportIncident: (data: {
    zone_id: string;
    incident_type: IncidentType;
    description: string;
    severity: Priority;
  }) =>
    request<IncidentAlert>(
      "/api/control-room/incidents/report",
      { method: "POST", body: JSON.stringify(data) },
      true
    ),

  // Wayfinding (public)
  getNavigationRoute: (data: {
    query: string;
    current_zone: string;
    language?: Language;
    avoid_zones?: string[];
    low_sensory_mode?: boolean;
  }) =>
    request<NavigationResponse>("/api/wayfinding/navigate", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Fan Assistant (public)
  sendChatMessage: (data: {
    message: string;
    language?: Language;
    session_id: string;
    fan_id?: string;
  }) =>
    request<ChatResponse>("/api/fan-assistant/chat", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Voice (public)
  createVoiceSession: (data: { fan_id: string; language?: Language }) =>
    request<VoiceSessionResponse>("/api/voice/session", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Crowd status (public)
  getCrowdStatus: (zoneIds?: string[]) => {
    const query = zoneIds?.length ? `?${zoneIds.map((z) => `zone_ids=${z}`).join("&")}` : "";
    return request<CrowdPredictionResponse>(`/api/crowd/status${query}`);
  },
};

export { ApiError };