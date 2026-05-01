from typing import Any

_TYPE_MAP = {
    "string": str,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _matches_type(value: Any, type_name: str) -> bool:
    if type_name == "number":
        return _is_number(value)
    expected = _TYPE_MAP.get(type_name)
    if expected is None:
        return False
    return isinstance(value, expected)


def _validate_object(value: Any, schema: dict[str, Any], path: str) -> tuple[bool, str | None]:
    if not isinstance(value, dict):
        return False, f"{path} must be object"

    required = schema.get("required", [])
    if not isinstance(required, list):
        return False, f"{path}.required must be array"

    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return False, f"{path}.properties must be object"

    for key in required:
        if key not in value:
            return False, f"{path}.{key} is required"

    for key, child_schema in properties.items():
        if key in value:
            ok, error = validate_schema(value[key], child_schema, f"{path}.{key}")
            if not ok:
                return False, error

    return True, None


def _validate_array(value: Any, schema: dict[str, Any], path: str) -> tuple[bool, str | None]:
    if not isinstance(value, list):
        return False, f"{path} must be array"

    items_schema = schema.get("items")
    if items_schema is None:
        return True, None

    for idx, item in enumerate(value):
        ok, error = validate_schema(item, items_schema, f"{path}[{idx}]")
        if not ok:
            return False, error

    return True, None


def validate_schema(
    value: Any,
    schema: dict[str, Any],
    path: str = "payload",
) -> tuple[bool, str | None]:
    if not isinstance(schema, dict):
        return False, f"{path} schema must be object"

    type_name = schema.get("type")
    if not isinstance(type_name, str):
        return False, f"{path}.type is required"

    if type_name not in _TYPE_MAP:
        return False, f"{path}.type '{type_name}' is not supported"

    if not _matches_type(value, type_name):
        return False, f"{path} must be {type_name}"

    if type_name == "object":
        return _validate_object(value, schema, path)
    if type_name == "array":
        return _validate_array(value, schema, path)

    return True, None
