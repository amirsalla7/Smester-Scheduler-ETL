import json

with open("config.json", "r") as f:
    config = json.load(f)

FIELD_MAP = config["fields"]
VALUE_MAP = config["values"]


def get_field(data, entity, field):
    possible_keys = FIELD_MAP.get(entity, {}).get(field, [])

    for key in possible_keys:
        if key in data:
            return data[key]

    return None


def normalize_value(category, value):
    if category in VALUE_MAP:
        return VALUE_MAP[category].get(value, value)
    return value