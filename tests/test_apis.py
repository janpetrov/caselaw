import os

import pytest
from dotenv import load_dotenv

from src.apis.anthropic import claude_infer
from src.apis.common import get_api_key
from src.apis.fireworks import fireworks_infer
from src.apis.google import gemini_infer
from src.apis.openai import openai_infer
from src.constants import (
    ANTHROPIC_API_KEY,
    FIREWORKS_API_KEY,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
)

TEST_MAX_TOKENS = 80


# Use pytest fixture to load environment variables once for the test session
@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
    yield


@pytest.mark.parametrize(
    "infer_func",
    [
        claude_infer,
        openai_infer,
        gemini_infer,
        fireworks_infer,
    ],
)
def test_all_apis(infer_func):
    prompt = "This is a test. Write just `hello` and nothing else."
    try:
        response = infer_func(prompt, max_tokens=TEST_MAX_TOKENS)

        assert isinstance(response, str)
        assert response.strip(), "Response should not be empty"
        assert "hello" in response, "Response should contain 'hello'"
    except Exception as e:
        pytest.fail(f"API {infer_func.__name__} failed with error: {str(e)}")


@pytest.mark.parametrize(
    "env_var",
    [
        ANTHROPIC_API_KEY,
        OPENAI_API_KEY,
        GOOGLE_API_KEY,
        FIREWORKS_API_KEY,
    ],
)
def test_api_key(env_var):
    env_key = os.getenv(env_var)
    assert env_key is not None, f"{env_var} should be set in the environment"
    get_key = get_api_key(key=None, key_name=env_var)
    assert get_key is not None, f"get_api_key should return a value for {env_var}"
    assert get_key == env_key, f"get_api_key should return the correct value for {env_var}"
