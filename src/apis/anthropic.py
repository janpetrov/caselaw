from functools import partial

import anthropic

from ..constants import ANTHROPIC_API_KEY, DEFAULT_MAX_TOKENS
from .common import get_api_key

CLAUDE_DEFAULT_MODEL = "claude-3-7-sonnet-20250219"


get_anthropic_api_key = partial(get_api_key, key_name=ANTHROPIC_API_KEY)


def claude_count_tokens(text: str, api_key: str | None = None) -> int:
    client = anthropic.Anthropic(api_key=get_anthropic_api_key(api_key))

    response = client.messages.count_tokens(
        model="claude-3-7-sonnet-20250219",
        system="You are a scientist",
        messages=[{"role": "user", "content": text}],
    )

    return response.input_tokens


def claude_infer(
    text: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1,
    top_k: int = 100,
    system: str | None = None,
    model: str = CLAUDE_DEFAULT_MODEL,
    api_key: str | None = None,
) -> str:
    client = anthropic.Anthropic(api_key=get_anthropic_api_key(api_key))
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_k=top_k,
        system=system if system is not None else anthropic.NOT_GIVEN,
        messages=[{"role": "user", "content": text}],
    )
    return message.content[0].text  # type: ignore
