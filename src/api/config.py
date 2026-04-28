"""
Application configuration loader.

L12: Human-readable config in YAML.
Loads config.yaml if present, falls back to environment variables.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Look for config.yaml in project root
_PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
_CONFIG_PATH: Path = _PROJECT_ROOT / "config.yaml"

_config: Optional[dict[str, object]] = None


def _load_config() -> dict[str, object]:
    """Load config from YAML file if available."""
    global _config
    if _config is not None:
        return _config

    if _CONFIG_PATH.exists():
        try:
            import yaml  # type: ignore[import-untyped]
            with open(_CONFIG_PATH) as f:
                _config = yaml.safe_load(f) or {}
            logger.info("Config loaded from %s", _CONFIG_PATH)
            return _config
        except ImportError:
            logger.warning("PyYAML not installed, falling back to env vars")
        except Exception:
            logger.warning("Failed to load config.yaml, falling back to env vars")

    _config = {}
    return _config


def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from config.yaml or environment variable."""
    config = _load_config()
    anthropic_config = config.get("anthropic", {})
    if isinstance(anthropic_config, dict):
        key = anthropic_config.get("api_key")
        if key and key != "YOUR_ANTHROPIC_API_KEY":
            return str(key)
    return os.environ.get("ANTHROPIC_API_KEY")


def get_anthropic_model() -> str:
    """Get the Claude model to use for extraction."""
    config = _load_config()
    anthropic_config = config.get("anthropic", {})
    if isinstance(anthropic_config, dict):
        model = anthropic_config.get("model")
        if model:
            return str(model)
    return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
