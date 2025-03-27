import pytest
from src.templates import load_template, render_template, get_templates_dir, get_template_env


def test_get_templates_dir():
    """Test that the templates directory is correctly identified."""
    templates_dir = get_templates_dir()
    assert templates_dir.exists(), "Templates directory does not exist"
    assert templates_dir.is_dir(), "Templates path is not a directory"
    assert templates_dir.name == "templates", "Directory name should be 'templates'"


def test_template_env():
    """Test that the template environment is created correctly."""
    env = get_template_env()
    assert env is not None, "Template environment should not be None"
    # Test calling it twice returns the same instance (singleton)
    env2 = get_template_env()
    assert env is env2, "Template environment should be a singleton"


def test_load_template():
    """Test loading a template."""
    # Load the test template
    template = load_template("test_template.jinja2")
    assert template is not None, "Template should not be None"

    # Test caching by loading it again
    template2 = load_template("test_template.jinja2")
    assert template is template2, "Templates should be cached"


def test_render_template():
    """Test rendering a template with context."""
    name = "World"
    data = {"item1": "value1", "item2": "value2"}

    rendered = render_template("test_template.jinja2", name=name, data=data)

    # Basic validation of rendered content
    assert f"Hello, {name}!" in rendered
    assert "item1: value1" in rendered
    assert "item2: value2" in rendered
