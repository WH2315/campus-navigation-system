from dataclasses import dataclass


@dataclass
class CampusNode:
    node_id: str
    name: str
    category: str
    intro: str
    indoor: bool
    crowded_score: float


@dataclass
class CampusEdge:
    from_id: str
    to_id: str
    distance: float
    indoor: bool
    crowded_score: float
