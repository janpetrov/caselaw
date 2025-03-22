import os


def get_api_key(key: str | None, key_name: str | None) -> str:
    if key is None and key_name is None:
        raise ValueError("Either key or key_name must be provided.")
    if key is not None:
        return key
    return os.environ[key_name]  # type: ignore
