"""Load YAML configuration once and expose a nested dict."""

from functools import lru_cache
from typing import Any

import yaml

from paths import CONFIG_PATH


@lru_cache(maxsize=1)
def load_settings() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def get_section(name: str) -> dict[str, Any]:
    return load_settings()[name]
