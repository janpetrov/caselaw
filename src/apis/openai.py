from openai import OpenAI


def openai_infer(
    text: str,
    max_tokens: int = 4000,
    temperature: float = 1,
    mini: bool = False
) -> str:
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini" if mini else "gpt-4",
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{
            "role": "user",
            "content": text
        }]
    )
    return completion.choices[0].message.content  # type: ignore
