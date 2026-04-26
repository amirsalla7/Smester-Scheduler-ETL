import json
import os
from typing import Any, Dict, List


CONFIG_FILE = os.path.join("web", "config.json")


def load_config() -> Dict[str, Any]:
    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")


CONFIG = load_config()


def reload_config():
    """
    Reload config.json at runtime if needed.
    """
    global CONFIG
    CONFIG = load_config()


def _normalize_key(key: Any) -> str:
    return str(key).strip().lower()


def _find_value_case_insensitive(row: Dict[str, Any], aliases: List[str]) -> Any:
    """
    Search for the first matching alias in row keys, case-insensitive.
    """
    if not isinstance(row, dict):
        return None

    normalized_row = {_normalize_key(k): v for k, v in row.items()}

    for alias in aliases:
        alias_norm = _normalize_key(alias)
        if alias_norm in normalized_row:
            return normalized_row[alias_norm]

    return None


def get_field(row: Dict[str, Any], entity: str, logical_field: str, default: Any = None) -> Any:
    """
    Extract a field from row based on aliases defined in config.json

    Example:
        get_field(row, "student", "name")
    """
    fields_config = CONFIG.get("fields", {})
    entity_config = fields_config.get(entity, {})
    aliases = entity_config.get(logical_field, [])

    if not aliases:
        return default

    value = _find_value_case_insensitive(row, aliases)
    return default if value is None else value


def normalize_value(category: str, value: Any) -> Any:
    """
    Normalize value using config.json mappings.

    Example:
        normalize_value("degree", "PhD") -> "Doctor"
    """
    if value is None:
        return value

    values_config = CONFIG.get("values", {})
    category_map = values_config.get(category, {})

    value_str = str(value).strip()
    return category_map.get(value_str, value)


def normalize_major(value: Any) -> Any:
    return normalize_value("major", value)


def normalize_degree(value: Any) -> Any:
    return normalize_value("degree", value)


def normalize_course_type(value: Any) -> Any:
    return normalize_value("course_type", value)


def normalize_room_type(value: Any) -> Any:
    return normalize_value("room_type", value)


def normalize_day(value: Any) -> Any:
    return normalize_value("day", value)