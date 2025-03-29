from functools import partial

from google import genai
from google.genai import types

from src.apis.common import get_api_key

from ..constants import DEFAULT_MAX_TOKENS, GOOGLE_API_KEY

get_google_api_key = partial(get_api_key, key_name=GOOGLE_API_KEY)


def gemini_infer(
    text: str,
    *,
    top_k: int = 40,
    top_p: float = 0.95,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1.0,
    api_key: str | None = None,
):
    client = genai.Client(api_key=get_google_api_key(api_key))

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        max_output_tokens=max_tokens,
        response_mime_type="text/plain",
    )

    return client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    ).text
