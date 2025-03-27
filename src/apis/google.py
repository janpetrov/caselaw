import os
from google import genai
from google.genai import types


def gemini_infer(text, top_k=40, top_p=0.95, temperature=1):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

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
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    return client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    ).text
