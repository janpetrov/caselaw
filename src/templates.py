import pathlib
from typing import Any

import jinja2

# Environment instance to be initialized once
_template_env = None


def get_templates_dir() -> pathlib.Path:
    """Returns the absolute path to the templates directory."""
    # Get the directory of the current file (templates.py)
    current_dir = pathlib.Path(__file__).parent
    # Go one directory up from src to the project root
    project_root = current_dir.parent
    # Return the path to the templates directory
    return project_root / "templates"


def get_template_env() -> jinja2.Environment:
    """Returns the Jinja2 environment, creating it if it doesn't exist."""
    global _template_env
    if _template_env is None:
        templates_dir = get_templates_dir()
        _template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )
    return _template_env


def load_template(template_name: str) -> jinja2.Template:
    """Loads a template by name from the templates directory."""
    env = get_template_env()
    return env.get_template(template_name)


def render_template(template_name: str, **kwargs: Any) -> str:
    """Loads and renders a template with the given context."""
    template = load_template(template_name)
    return template.render(**kwargs)
