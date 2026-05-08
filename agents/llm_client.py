import json
import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMConfigError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith("replace_with") or value.endswith("replace_me"):
        raise LLMConfigError(
            f"Missing required environment variable: {name}. "
            "Create .env from .env.example and provide a real MiniGPT/meinGPT value."
        )
    return value


class MiniGPTClient:
    def __init__(self) -> None:
        self.api_key = _required_env("MINIGPT_API_KEY")
        self.model = _required_env("MINIGPT_MODEL")
        self.chat_url = os.getenv(
            "MINIGPT_CHAT_URL",
            "https://app.meingpt.com/api/openai/v1/chat/completions",
        ).strip()
        self.temperature = float(os.getenv("MINIGPT_TEMPERATURE", "0.1"))
        self.timeout = int(os.getenv("MINIGPT_TIMEOUT_SECONDS", "60"))

    def chat(self, system: str, user: str, response_format: Optional[Dict[str, str]] = None) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "stream": False,
        }
        if response_format:
            payload["response_format"] = response_format

        response = requests.post(
            self.chat_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise LLMResponseError(f"LLM API returned HTTP {response.status_code}: {response.text[:1000]}")

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMResponseError(f"Unexpected LLM response shape: {json.dumps(data)[:1000]}") from exc

    def chat_json(self, system: str, user: str) -> Dict[str, Any]:
        content = self.chat(system, user, response_format={"type": "json_object"})
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMResponseError(f"LLM did not return valid JSON. Raw content: {content[:1000]}") from exc
