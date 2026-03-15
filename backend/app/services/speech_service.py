from __future__ import annotations

from typing import Optional

import httpx

from app.config import settings


class SpeechService:
    async def tts(self, text: str, voice: str) -> tuple[str, float]:
        # 这里返回 mock 结果，后续可替换为真实 TTS 平台。
        words = max(1, len(text))
        duration = round(words / 12.0, 2)
        if settings.tts_engine == "none":
            return "", 0.0
        return f"https://mock-tts.local/audio/{voice}?len={words}", duration

    async def asr(self, audio_bytes: bytes, filename: str, language: str = "zh") -> str:
        if settings.asr_engine == "mock" or not settings.openai_api_key.strip():
            # mock 模式只返回固定识别结果，便于联调全流程。
            return "请介绍一下图书馆的学习资源和开放时间。"

        url = f"{settings.openai_base_url.rstrip('/')}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        data = {
            "model": settings.openai_model,
            "language": language,
        }
        files = {
            "file": (filename or "voice.wav", audio_bytes, "audio/wav"),
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=headers, data=data, files=files)
                resp.raise_for_status()
                payload = resp.json()
                text: Optional[str] = payload.get("text")
                return (text or "").strip() or "未识别到有效语音内容。"
        except Exception:
            return "语音识别服务暂时不可用，请稍后重试。"
