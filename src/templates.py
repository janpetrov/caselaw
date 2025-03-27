import pathlib
import jinja2

# Template cache dictionary to store loaded templates
_template_cache = {}
# Environment instance to be initialized once
_template_env = None


def get_templates_dir():
    """
    Returns the absolute path to the templates directory.
    """
    # Get the directory of the current file (templates.py)
    current_dir = pathlib.Path(__file__).parent
    # Go one directory up from src to the project root
    project_root = current_dir.parent
    # Return the path to the templates directory
    return project_root / "templates"


def get_template_env():
    """
    Returns the Jinja2 environment, creating it if it doesn't exist.
    """
    global _template_env
    if _template_env is None:
        templates_dir = get_templates_dir()
        _template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )
    return _template_env


def load_template(template_name):
    """
    Loads a template by name from the templates directory.
    Uses cache if template was previously loaded.

    Args:
        template_name (str): Name of the template file

    Returns:
        jinja2.Template: The loaded template
    """
    # Check if template is in cache
    if template_name not in _template_cache:
        # If not, load it and add to cache
        env = get_template_env()
        _template_cache[template_name] = env.get_template(template_name)

    # Return from cache
    return _template_cache[template_name]


def render_template(template_name, **kwargs):
    """
    Loads and renders a template with the given context.
    Uses template caching for better performance.

    Args:
        template_name (str): Name of the template file
        **kwargs: Variables to pass to the template

    Returns:
        str: The rendered template content
    """
    template = load_template(template_name)
    return template.render(**kwargs)


# Example usage:
# prompt = render_template("extract_acts_01.jinja2", court_opinion=court_opinion_text)
