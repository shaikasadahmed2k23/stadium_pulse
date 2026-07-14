"""
Wayfinding Agent (Feature 2 + 7).
Takes a natural-language navigation request, builds a route across
a simplified stadium graph, and avoids congested zones using live
data from the Crowd Intelligence Agent. Supports low-sensory mode
for accessibility (avoids loud/high-stimulus zones).
"""
from agents.base_agent import BaseAgent
from agents.crowd_intelligence_agent import CrowdIntelligenceAgent
from models.schemas import (
    NavigationRequest,
    NavigationResponse,
    NavigationStep,
    ZoneStatus,
)
from services.stadium_graph import stadium_graph


class WayfindingAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="WayfindingAgent")
        self.crowd_agent = CrowdIntelligenceAgent()

    async def process(self, request: NavigationRequest) -> NavigationResponse:
        # Step 1: understand intent (destination) from natural language
        destination_zone = await self._extract_destination(request.query, request.language.value)

        # Step 2: get live congestion data to inform routing
        crowd_data = await self.crowd_agent.process()
        congestion_map = {z.zone_id: z.status for z in crowd_data.zones}

        # Step 3: build route avoiding congested + excluded zones
        avoid_zones = set(request.avoid_zones)
        if request.low_sensory_mode:
            avoid_zones.update(stadium_graph.high_stimulus_zones())

        route_zone_ids = stadium_graph.find_route(
            start=request.current_zone,
            end=destination_zone,
            avoid_zones=avoid_zones,
            congestion_map=congestion_map,
        )

        steps = self._build_steps(route_zone_ids, congestion_map)
        total_time = sum(s.estimated_time_seconds for s in steps)
        avoided_congestion = not any(
            s.congestion_level in (ZoneStatus.ELEVATED, ZoneStatus.CRITICAL) for s in steps
        )

        self.log_reasoning(
            decision=f"Route to {destination_zone} via {len(steps)} steps",
            factors=[
                {"factor": "low_sensory_mode", "weight": 0.6, "value": str(request.low_sensory_mode)},
                {"factor": "avoided_congestion", "weight": 0.8, "value": str(avoided_congestion)},
                {"factor": "zones_excluded", "weight": 0.4, "value": str(len(avoid_zones))},
            ],
        )

        return NavigationResponse(
            route=steps,
            total_estimated_time_seconds=total_time,
            route_avoids_congestion=avoided_congestion,
        )

    async def _extract_destination(self, query: str, language: str) -> str:
        """Uses Gemini to map free-text query -> a known zone_id."""
        known_zones = ", ".join(stadium_graph.all_zone_ids())
        system_instruction = (
            "You are a stadium navigation intent parser. Given a fan's request "
            f"in language '{language}', return ONLY the single most likely zone_id "
            f"from this list: [{known_zones}]. Return just the zone_id, nothing else."
        )
        response = await self._call_gemini(prompt=query, system_instruction=system_instruction)
        cleaned = response.strip().lower()
        return cleaned if cleaned in stadium_graph.all_zone_ids() else stadium_graph.default_zone()

    def _build_steps(self, zone_ids: list[str], congestion_map: dict) -> list[NavigationStep]:
        steps = []
        for zone_id in zone_ids:
            zone_info = stadium_graph.get_zone_info(zone_id)
            congestion = congestion_map.get(zone_id, ZoneStatus.NORMAL)
            steps.append(
                NavigationStep(
                    instruction=zone_info["instruction"],
                    zone=zone_id,
                    estimated_time_seconds=zone_info["base_time_seconds"],
                    congestion_level=congestion,
                )
            )
        return steps