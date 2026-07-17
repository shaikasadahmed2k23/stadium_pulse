"""
Simplified stadium navigation graph. In a real system this would be
a proper weighted graph with pathfinding (Dijkstra/A*); for a hackathon
demo, an adjacency map with a BFS-based route + congestion-aware
detour logic is enough to show the concept clearly and reliably.
"""
from collections import deque

GRAPH = {
    "gate_1": {"neighbors": ["concourse_a"], "instruction": "Enter through Gate 1", "base_time_seconds": 30, "high_stimulus": True},
    "gate_2": {"neighbors": ["concourse_b"], "instruction": "Enter through Gate 2", "base_time_seconds": 30, "high_stimulus": True},
    "gate_3": {"neighbors": ["concourse_a"], "instruction": "Enter through Gate 3", "base_time_seconds": 30, "high_stimulus": True},
    "concourse_a": {"neighbors": ["gate_1", "gate_3", "section_101", "concourse_b"], "instruction": "Walk through Concourse A", "base_time_seconds": 60, "high_stimulus": True},
    "concourse_b": {"neighbors": ["gate_2", "concourse_a", "section_101"], "instruction": "Walk through Concourse B", "base_time_seconds": 60, "high_stimulus": True},
    "section_101": {"neighbors": ["concourse_a", "concourse_b"], "instruction": "Arrive at Section 101", "base_time_seconds": 20, "high_stimulus": False},
}


class StadiumGraph:
    def all_zone_ids(self) -> list[str]:
        return list(GRAPH.keys())

    def default_zone(self) -> str:
        return "section_101"

    def get_zone_info(self, zone_id: str) -> dict:
        return GRAPH.get(zone_id, GRAPH[self.default_zone()])

    def high_stimulus_zones(self) -> set[str]:
        return {zid for zid, z in GRAPH.items() if z.get("high_stimulus")}

    def find_route(
        self,
        start: str,
        end: str,
        avoid_zones: set[str],
        congestion_map: dict,
    ) -> list[str]:
        """
        BFS pathfinding with a soft preference against CRITICAL congestion zones.
        Falls back to allowing them if no other path exists (better a slow
        route than no route).
        """
        if start not in GRAPH or end not in GRAPH:
            return [end]

        route = self._bfs(start, end, avoid_zones | self._critical_zones(congestion_map))
        if route is None:
            # fallback: ignore congestion, just avoid explicitly excluded zones
            route = self._bfs(start, end, avoid_zones)
        if route is None:
            # last resort: direct, ignore all restrictions
            route = self._bfs(start, end, set())
        return route or [end]

    def _critical_zones(self, congestion_map: dict) -> set[str]:
        from shared.schemas import ZoneStatus
        return {zid for zid, status in congestion_map.items() if status == ZoneStatus.CRITICAL}

    def _bfs(self, start: str, end: str, blocked: set[str]) -> list[str] | None:
        if start == end:
            return [start]

        visited = {start}
        queue = deque([[start]])

        while queue:
            path = queue.popleft()
            current = path[-1]

            for neighbor in GRAPH.get(current, {}).get("neighbors", []):
                if neighbor in blocked or neighbor in visited:
                    continue
                new_path = path + [neighbor]
                if neighbor == end:
                    return new_path
                visited.add(neighbor)
                queue.append(new_path)

        return None


stadium_graph = StadiumGraph()
