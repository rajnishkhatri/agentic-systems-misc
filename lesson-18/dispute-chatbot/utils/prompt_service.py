"""Jinja2 template rendering service for prompt management.

Reused from composable_app with minimal adaptation for dispute-chatbot.
Follows the {ClassName}_{method}.j2 naming convention for prompts.
"""

import json
import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

# Template directory relative to this file
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Jinja2 environment with file system loader
env = Environment(loader=FileSystemLoader(PROMPTS_DIR))


def render_prompt(template_name: str, **kwargs: Any) -> str:
    """Render a Jinja2 template with provided variables.

    Args:
        template_name: Name of the template file (e.g., 'DisputeClassifier_classify.j2')
        **kwargs: Variables to pass to the template

    Returns:
        Rendered prompt string

    Raises:
        TypeError: If template_name is not a string
        ValueError: If template_name is empty
        jinja2.TemplateNotFound: If template file doesn't exist
    """
    # Step 1: Type checking
    if not isinstance(template_name, str):
        raise TypeError("template_name must be a string")

    # Step 2: Input validation
    if not template_name.strip():
        raise ValueError("template_name cannot be empty")

    # Step 3: Main logic
    template = env.get_template(template_name)
    rendered = template.render(**kwargs)
    logger.debug(json.dumps({"template": template_name, "variables": list(kwargs.keys())}))
    return rendered
