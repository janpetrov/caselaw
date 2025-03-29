from functools import partial

from openai import OpenAI

from ..constants import DEFAULT_MAX_TOKENS, OPENAI_API_KEY
from .common import get_api_key

get_openai_api_key = partial(get_api_key, key_name=OPENAI_API_KEY)


def openai_infer(
    text: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1,
    mini: bool = False,
    api_key: str | None = None,
) -> str:
    client = OpenAI(api_key=get_openai_api_key(api_key))
    completion = client.chat.completions.create(
        model="gpt-4o-mini" if mini else "gpt-4",
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": text}],
    )
    return completion.choices[0].message.content  # type: ignore
