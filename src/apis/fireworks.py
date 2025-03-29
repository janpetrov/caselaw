import json
from functools import partial

import requests

from ..constants import DEFAULT_MAX_TOKENS, FIREWORKS_API_KEY
from .common import get_api_key

FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORKS_DEFAULT_MODEL = "deepseek-v3"


get_fireworks_api_key = partial(get_api_key, key_name=FIREWORKS_API_KEY)


def fireworks_infer(
    text: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.6,
    top_k: int = 100,
    top_p: float = 1.0,
    model: str = FIREWORKS_DEFAULT_MODEL,
    api_key: str | None = None,
) -> str | None:
    url = FIREWORKS_URL
    payload = {
        "model": f"accounts/fireworks/models/{model}",
        "max_tokens": max_tokens,
        "top_p": top_p,
        "top_k": top_k,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": temperature,
        "messages": [{"role": "user", "content": text}],
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_fireworks_api_key(api_key)}",
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    try:
        return response.json()["choices"][0]["message"]["content"]
    except KeyError:
        return None
