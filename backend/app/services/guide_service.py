import json
from pathlib import Path
from typing import List

from app.schemas import GuideGenerateResponse, SpotGuideResponse, SpotInfo
from app.services.aigc_service import AIGCService


class GuideService:
    def __init__(self) -> None:
        data_dir = Path(__file__).resolve().parent.parent / "data"
        with open(data_dir / "campus_nodes.json", "r", encoding="utf-8") as f:
            self.nodes = {item["node_id"]: item for item in json.load(f)}
        self.aigc = AIGCService()

    def list_spots(self) -> List[SpotInfo]:
        spots: List[SpotInfo] = []
        for node_id, node in self.nodes.items():
            spots.append(
                SpotInfo(
                    node_id=node_id,
                    name=node["name"],
                    category=node["category"],
                    intro=node["intro"],
                )
            )
        return spots

    def _fallback_script(self, language: str, user_profile: str, style: str, route_nodes: List[str]) -> GuideGenerateResponse:
        route_names = [self.nodes[node_id]["name"] for node_id in route_nodes if node_id in self.nodes]
        intros = [self.nodes[node_id]["intro"] for node_id in route_nodes if node_id in self.nodes]

        if language == "en":
            title = "AI Campus Tour"
            script = (
                f"Welcome to this {style} campus tour for {user_profile}. "
                f"Today's route includes: {', '.join(route_names)}. "
                f"Highlights: {' '.join(intros)}"
            )
        else:
            title = "校园智能导览"
            script = (
                f"欢迎参加本次{style}风格导览，面向用户类型为{user_profile}。"
                f"本次路线依次经过：{'、'.join(route_names)}。"
                f"重点介绍：{' '.join(intros)}"
            )

        return GuideGenerateResponse(title=title, script=script)

    async def generate(self, language: str, user_profile: str, style: str, route_nodes: List[str]) -> GuideGenerateResponse:
        fallback = self._fallback_script(language, user_profile, style, route_nodes)

        route_json = []
        for node_id in route_nodes:
            node = self.nodes.get(node_id)
            if node:
                route_json.append({"name": node["name"], "intro": node["intro"], "category": node["category"]})

        if language == "en":
            system_prompt = "You are a campus virtual guide. Produce concise, engaging, factual scripts."
            user_prompt = (
                "Generate a single English tour script with clear transitions. "
                f"Audience: {user_profile}. Style: {style}. Spots: {route_json}."
            )
            title = "AI Campus Tour"
        else:
            system_prompt = "你是一名高校虚拟导览讲解员，请生成自然、连贯、信息准确的中文讲解词。"
            user_prompt = (
                f"请面向{user_profile}用户，使用{style}风格，基于以下景点生成一段完整讲解词：{route_json}。"
                "要求：语言自然，段落衔接流畅，包含校园文化与学习生活信息。"
            )
            title = "校园智能导览"

        text = await self.aigc.chat(system_prompt, user_prompt, temperature=0.75)
        if not text:
            return fallback

        return GuideGenerateResponse(title=title, script=text)

    async def answer_question(self, question: str, language: str, current_spot: str | None) -> str:
        spot_context = self.nodes.get(current_spot, {}) if current_spot else {}
        if language == "en":
            system_prompt = "You are a helpful campus tour assistant. Keep answers short and clear."
            user_prompt = f"Question: {question}. Spot context: {spot_context}"
            fallback = "Based on the current spot information, this location supports study, culture, and campus activities."
        else:
            system_prompt = "你是校园导览问答助手，请给出简洁且准确的中文回答。"
            user_prompt = f"问题：{question}。当前景点上下文：{spot_context}"
            fallback = "根据当前景点信息，这里兼具学习、文化展示和校园活动功能。"

        text = await self.aigc.chat(system_prompt, user_prompt, temperature=0.5)
        return text or fallback

    async def generate_spot_guide(
        self,
        node_id: str,
        language: str,
        user_profile: str,
        style: str,
    ) -> SpotGuideResponse:
        node = self.nodes.get(node_id)
        if not node:
            raise ValueError(f"Unknown node_id: {node_id}")

        if language == "en":
            fallback = SpotGuideResponse(
                title=f"Spot Guide: {node['name']}",
                script=f"{node['name']} is a {node['category']} spot. {node['intro']}",
            )
            system_prompt = "You are a campus guide. Generate concise, vivid spot narration."
            user_prompt = (
                f"Generate one short narration for spot {node['name']} ({node['category']}). "
                f"Audience: {user_profile}. Style: {style}. Base info: {node['intro']}"
            )
            title = f"Spot Guide: {node['name']}"
        else:
            fallback = SpotGuideResponse(
                title=f"景点讲解：{node['name']}",
                script=f"{node['name']}属于{node['category']}区域。{node['intro']}",
            )
            system_prompt = "你是校园景点讲解员，请输出简洁、有画面感、信息准确的中文单景点讲解词。"
            user_prompt = (
                f"请为景点“{node['name']}”生成一段单景点讲解词。"
                f"用户类型：{user_profile}，讲解风格：{style}，基础信息：{node['intro']}。"
                "要求：80到140字，包含功能与校园文化价值。"
            )
            title = f"景点讲解：{node['name']}"

        text = await self.aigc.chat(system_prompt, user_prompt, temperature=0.7)
        if not text:
            return fallback
        return SpotGuideResponse(title=title, script=text)
