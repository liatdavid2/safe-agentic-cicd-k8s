import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    api_key = os.getenv("MINIGPT_API_KEY", "").strip()
    models_url = os.getenv("MINIGPT_MODELS_URL", "https://app.meingpt.com/api/models/v1").strip()
    if not api_key or api_key.endswith("replace_me"):
        print("MINIGPT_API_KEY is missing. Create .env from .env.example first.")
        return 1

    response = requests.get(
        models_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60,
    )
    if response.status_code >= 400:
        print(f"Failed to list models: HTTP {response.status_code}")
        print(response.text)
        return 1

    data = response.json()
    for model in data.get("models", []):
        model_id = model.get("id", "")
        name = model.get("name", "")
        provider = model.get("provider", "")
        family = model.get("family", "")
        print(f"{model_id}\t{name}\t{provider}\t{family}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
