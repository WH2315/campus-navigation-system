from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class RoutePlanRequest(BaseModel):
    start_id: str = Field(..., description="起点节点ID")
    end_id: str = Field(..., description="终点节点ID")
    avoid_crowded: bool = Field(default=False, description="是否尽量避开拥挤区域")
    prefer_indoor: bool = Field(default=False, description="是否优先室内路线")


class RouteSegment(BaseModel):
    from_id: str
    to_id: str
    distance: float


class RoutePlanResponse(BaseModel):
    node_path: List[str]
    total_distance: float
    estimated_minutes: int
    segments: List[RouteSegment]


class GuideGenerateRequest(BaseModel):
    user_profile: Literal["new_student", "parent", "visitor", "alumni"] = "visitor"
    style: Literal["formal", "friendly", "storytelling"] = "friendly"
    language: Literal["zh", "en"] = "zh"
    route_nodes: List[str]


class GuideGenerateResponse(BaseModel):
    title: str
    script: str


class ChatRequest(BaseModel):
    question: str
    language: Literal["zh", "en"] = "zh"
    current_spot_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str


class TTSRequest(BaseModel):
    text: str
    voice: str = "xiaoyan"


class TTSResponse(BaseModel):
    audio_url: str
    duration_sec: float


class ASRResponse(BaseModel):
    text: str


class VoiceChatResponse(BaseModel):
    transcript: str
    answer: str


class SpotInfo(BaseModel):
    node_id: str
    name: str
    category: str
    intro: str


class SpotListResponse(BaseModel):
    spots: List[SpotInfo]


class SpotGuideRequest(BaseModel):
    node_id: str
    user_profile: Literal["new_student", "parent", "visitor", "alumni"] = "visitor"
    style: Literal["formal", "friendly", "storytelling"] = "friendly"
    language: Literal["zh", "en"] = "zh"


class SpotGuideResponse(BaseModel):
    title: str
    script: str
