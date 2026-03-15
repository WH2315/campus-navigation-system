import heapq
import json
from pathlib import Path
from typing import Dict, List, Tuple

from app.schemas import RoutePlanResponse, RouteSegment


class RouteService:
    def __init__(self) -> None:
        data_dir = Path(__file__).resolve().parent.parent / "data"
        with open(data_dir / "campus_nodes.json", "r", encoding="utf-8") as f:
            self.nodes = {item["node_id"]: item for item in json.load(f)}
        with open(data_dir / "campus_edges.json", "r", encoding="utf-8") as f:
            self.edges = json.load(f)

        self.graph: Dict[str, List[dict]] = {}
        for edge in self.edges:
            self.graph.setdefault(edge["from_id"], []).append(edge)
            # 无向图：反向边镜像
            reverse = {
                "from_id": edge["to_id"],
                "to_id": edge["from_id"],
                "distance": edge["distance"],
                "indoor": edge["indoor"],
                "crowded_score": edge["crowded_score"],
            }
            self.graph.setdefault(reverse["from_id"], []).append(reverse)

    def _edge_cost(self, edge: dict, avoid_crowded: bool, prefer_indoor: bool) -> float:
        cost = float(edge["distance"])
        if avoid_crowded:
            cost += float(edge["crowded_score"]) * 5.0
        if prefer_indoor and not bool(edge["indoor"]):
            cost += 15.0
        return cost

    def plan(self, start_id: str, end_id: str, avoid_crowded: bool, prefer_indoor: bool) -> RoutePlanResponse:
        if start_id not in self.nodes:
            raise ValueError(f"Unknown start_id: {start_id}")
        if end_id not in self.nodes:
            raise ValueError(f"Unknown end_id: {end_id}")

        dist: Dict[str, float] = {node_id: float("inf") for node_id in self.nodes}
        prev: Dict[str, str] = {}
        prev_edge: Dict[str, dict] = {}

        dist[start_id] = 0.0
        pq: List[Tuple[float, str]] = [(0.0, start_id)]

        while pq:
            cur_dist, cur = heapq.heappop(pq)
            if cur_dist > dist[cur]:
                continue
            if cur == end_id:
                break
            for edge in self.graph.get(cur, []):
                nxt = edge["to_id"]
                w = self._edge_cost(edge, avoid_crowded, prefer_indoor)
                nd = cur_dist + w
                if nd < dist[nxt]:
                    dist[nxt] = nd
                    prev[nxt] = cur
                    prev_edge[nxt] = edge
                    heapq.heappush(pq, (nd, nxt))

        if dist[end_id] == float("inf"):
            raise ValueError("No path found between nodes")

        node_path: List[str] = []
        cur = end_id
        while cur in prev:
            node_path.append(cur)
            cur = prev[cur]
        node_path.append(start_id)
        node_path.reverse()

        segments: List[RouteSegment] = []
        total_distance = 0.0
        for node in node_path[1:]:
            edge = prev_edge[node]
            d = float(edge["distance"])
            total_distance += d
            segments.append(
                RouteSegment(
                    from_id=edge["from_id"],
                    to_id=edge["to_id"],
                    distance=d,
                )
            )

        estimated_minutes = max(1, int(round(total_distance / 75.0)))
        return RoutePlanResponse(
            node_path=node_path,
            total_distance=round(total_distance, 2),
            estimated_minutes=estimated_minutes,
            segments=segments,
        )
