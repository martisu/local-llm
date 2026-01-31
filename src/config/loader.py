"""Configuration loader with Jinja2 templating and environment variable substitution."""

import os
import re
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

from .schema import AppConfig


def substitute_env_vars(content: str) -> str:
    """Substitute ${ENV_VAR:default} patterns with environment variables."""
    pattern = r'\$\{(\w+)(?::([^}]*))?\}'

    def replace(match):
        var_name = match.group(1)
        default_value = match.group(2) or ""
        return os.environ.get(var_name, default_value)

    return re.sub(pattern, replace, content)


def load_config(config_path: str = None) -> AppConfig:
    """Load and validate application configuration."""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"

    with open(config_path, 'r') as f:
        raw_content = f.read()

    env = Environment(
        loader=FileSystemLoader(str(Path(config_path).parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.from_string(raw_content)
    rendered = template.render()
    rendered = substitute_env_vars(rendered)

    config_dict = yaml.safe_load(rendered)
    config = AppConfig.model_validate(config_dict)
    return config


def get_backend_url() -> str:
    """Get the backend URL."""
    config = load_config()
    return config.backend.base_url


def get_model_name() -> str:
    """Get the model name."""
    config = load_config()
    return config.backend.model


if __name__ == "__main__":
    config = load_config()
    print(f"Backend: {config.backend.type}")
    print(f"Model: {config.backend.model}")
    print(f"URL: {config.backend.base_url}")
