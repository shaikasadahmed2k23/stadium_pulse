// Shared TypeScript types mirroring backend Pydantic schemas

export type ZoneStatus = "normal" | "elevated" | "critical";
export type Language = "en" | "es" | "fr" | "pt" | "ar" | "hi";
export type IncidentType = "crowd_surge" | "lost_person" | "medical" | "security";
export type Priority = "low" | "medium" | "high" | "critical";

export interface ZoneData {
  zone_id: string;
  zone_name: string;
  current_occupancy: number;
  max_capacity: number;
  occupancy_percentage: number;
  status: ZoneStatus;
  predicted_occupancy_10min: number | null;
  timestamp: string;
}

export interface ReasoningFactor {
  factor: string;
  weight: number;
  value: string;
}

export interface ReasoningEntry {
  id: string;
  agent: string;
  decision: string;
  factors: ReasoningFactor[];
  timestamp: string;
}

export interface DecisionRecommendation {
  recommendation_id: string;
  action: string;
  affected_zones: string[];
  confidence_score: number;
  reasoning_factors: ReasoningFactor[];
  priority: Priority;
  timestamp: string;
}

export interface IncidentAlert {
  incident_id: string;
  incident_type: IncidentType;
  zone: string;
  description: string;
  auto_detected: boolean;
  suggested_action: string;
  severity: Priority;
  timestamp: string;
}

export interface ControlRoomState {
  zones: ZoneData[];
  active_recommendations: DecisionRecommendation[];
  active_incidents: IncidentAlert[];
}

export interface CrowdPredictionResponse {
  zones: ZoneData[];
  highest_risk_zone: string | null;
  overall_status: ZoneStatus;
}

export interface NavigationStep {
  instruction: string;
  zone: string;
  estimated_time_seconds: number;
  congestion_level: ZoneStatus;
}

export interface NavigationResponse {
  route: NavigationStep[];
  total_estimated_time_seconds: number;
  route_avoids_congestion: boolean;
}

export interface ChatResponse {
  reply: string;
  detected_intent: string | null;
  routed_to_wayfinding: boolean;
  session_id: string;
}

export interface VoiceSessionResponse {
  room_name: string;
  livekit_token: string;
  livekit_url: string;
}