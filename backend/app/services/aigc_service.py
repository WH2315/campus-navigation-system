from __future__ import annotations

from typing import Optional

import httpx

from app.config import settings


class AIGCService:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key.strip()
        self.base_url = settings.openai_base_url.rstrip("/")
        self.model = settings.openai_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> Optional[str]:
        if not self.enabled:
            return None

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return None
