import inspect
from typing import Annotated, Optional, Union, get_type_hints, get_origin, get_args

from .types import FieldInfo


def Field(
        description: str = "",
        *,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        exclusive_minimum: Optional[float] = None,
        exclusive_maximum: Optional[float] = None,
        multiple_of: Optional[float] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        enum: Optional[list] = None,
        format: Optional[str] = None,
        examples: Optional[list] = None,
        **extra
) -> FieldInfo:
    """Create field information"""
    return FieldInfo(
        description=description,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        minimum=minimum,
        maximum=maximum,
        exclusive_minimum=exclusive_minimum,
        exclusive_maximum=exclusive_maximum,
        multiple_of=multiple_of,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        enum=enum,
        format=format,
        examples=examples,
        extra=extra if extra else None
    )


type_mapping = {
    int: {"type": "integer"},
    float: {"type": "number"},
    str: {"type": "string"},
    bool: {"type": "boolean"},
    list: {"type": "array"},
    dict: {"type": "object"},
    type(None): {"type": "null"},
}


def python_type_to_json_type(py_type) -> dict:
    """Convert Python type to JSON Schema type"""
    origin = get_origin(py_type)
    args = get_args(py_type)

    # Process basic types
    if py_type in type_mapping:
        return type_mapping[py_type].copy()

    # Process Optional[T] or Union[T, None]
    if origin is Union:
        non_none_types = [t for t in args if t is not type(None)]
        has_none = type(None) in args

        if len(non_none_types) == 1:
            schema = python_type_to_json_type(non_none_types[0])
            if has_none:
                # Optional type
                return {"anyOf": [schema, {"type": "null"}]}
            return schema
        else:
            # Union of multiple types
            return {"anyOf": [python_type_to_json_type(t) for t in non_none_types]}

    # Process List[T]
    if origin is list:
        schema: dict = {"type": "array"}
        if args:
            schema["items"] = python_type_to_json_type(args[0])
        return schema

    # Process Dict[K, V]
    if origin is dict:
        schema: dict = {"type": "object"}
        if len(args) == 2:
            schema["additionalProperties"] = python_type_to_json_type(args[1])
        return schema

    # Default return object type
    return {"type": "object"}


def extract_field_info(annotation) -> tuple:
    """
    Extract base type and field info from Annotated type
    Returns: (base_type, field_info)
    """
    origin = get_origin(annotation)

    if origin is Annotated:
        args = get_args(annotation)
        # Find FieldInfo
        field_info = None
        if len(args) == 2:
            base_type, field_info = args
            if isinstance(args[1], FieldInfo):
                field_info = args[1]
            elif isinstance(args[1], str):
                field_info = Field(description=args[1])
        else:
            base_type = args[0]

        return base_type, field_info

    return annotation, None


def apply_field_constraints(schema: dict, field_info: FieldInfo) -> dict:
    """Apply field constraints to JSON Schema"""
    if not field_info:
        return schema

    # Description
    if field_info.description:
        schema["description"] = field_info.description

    # String constraints
    if field_info.min_length is not None:
        schema["minLength"] = field_info.min_length
    if field_info.max_length is not None:
        schema["maxLength"] = field_info.max_length
    if field_info.pattern:
        schema["pattern"] = field_info.pattern

    # Numeric constraints
    if field_info.minimum is not None:
        schema["minimum"] = field_info.minimum
    if field_info.maximum is not None:
        schema["maximum"] = field_info.maximum
    if field_info.exclusive_minimum is not None:
        schema["exclusiveMinimum"] = field_info.exclusive_minimum
    if field_info.exclusive_maximum is not None:
        schema["exclusiveMaximum"] = field_info.exclusive_maximum
    if field_info.multiple_of is not None:
        schema["multipleOf"] = field_info.multiple_of

    # Array constraints
    if field_info.min_items is not None:
        schema["minItems"] = field_info.min_items
    if field_info.max_items is not None:
        schema["maxItems"] = field_info.max_items
    if field_info.unique_items is not None:
        schema["uniqueItems"] = field_info.unique_items

    # Enum
    if field_info.enum:
        schema["enum"] = field_info.enum

    # Format
    if field_info.format:
        schema["format"] = field_info.format

    # Examples
    if field_info.examples:
        schema["examples"] = field_info.examples

    # Additional properties
    if field_info.extra:
        schema.update(field_info.extra)

    return schema


def func_to_json_schema(func) -> dict:
    """
    Convert function to JSON Schema
    Supports Annotated type annotations and custom Field
    """
    sig = inspect.signature(func)

    # Get type hints (including Annotated)
    try:
        type_hints = get_type_hints(func, include_extras=True)
    except:
        type_hints = func.__annotations__

    schema = {
        "type": "object",
        "properties": {},
        "required": [],
        "title": func.__name__
    }

    # Add function documentation
    doc = inspect.getdoc(func)
    if doc:
        schema["description"] = doc

    for param_name, param in sig.parameters.items():
        # Skip *args and **kwargs
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        annotation = type_hints.get(param_name, str)

        # Extract base type and field info
        base_type, field_info = extract_field_info(annotation)

        # Convert to JSON Schema type
        prop_schema = python_type_to_json_type(base_type)

        # Apply field constraints
        prop_schema = apply_field_constraints(prop_schema, field_info)

        # Handle default values
        if param.default != inspect.Parameter.empty:
            prop_schema["default"] = param.default
        else:
            schema["required"].append(param_name)

        schema["properties"][param_name] = prop_schema

    return schema


def func_to_arguments(func) -> list:
    sig = inspect.signature(func)
    try:
        type_hints = get_type_hints(func, include_extras=True)
    except:
        type_hints = func.__annotations__
    arguments = []
    for param_name, param in sig.parameters.items():
        # Skip *args and **kwargs
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        argument: dict = {
            "name": param_name,
        }
        annotation = type_hints.get(param_name, str)
        _, field_info = extract_field_info(annotation)
        if field_info:
            argument["description"] = field_info.description
        # Extract base type and field info
        if param.default == inspect.Parameter.empty:
            argument["required"] = True
        arguments.append(argument)
    return arguments
