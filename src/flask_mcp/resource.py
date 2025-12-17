import json
import re
from typing import Any, Callable, Optional, Union, List, Dict
from urllib.parse import parse_qs, unquote

from pydantic import Field

from .types import Resource as _Resource, ResourceGetResult


class Resource(_Resource):
    """
    Resource class
    """
    func: Callable[..., Any] = Field(exclude=True)
    arguments: List[Dict] = Field(exclude=True)

    def definition(self):
        res: dict[str, Any] = {
            "uri": self.uri,
            "name": self.name,
        }

        if self.mimeType:
            res["mimeType"] = self.mimeType
        if self.title:
            res["title"] = self.title
        if self.description:
            res["description"] = self.description
        if self.icons:
            res["icons"] = self.icons
        return res


def resource_func_result(resource: Resource):
    return resource_template_func_result(resource, {})


class ResourceTemplate(Resource):

    def definition(self):
        res: dict[str, Any] = {
            "uriTemplate": self.uri,
            "name": self.name,
        }
        if self.mimeType:
            res["mimeType"] = self.mimeType
        if self.title:
            res["title"] = self.title
        if self.description:
            res["description"] = self.description
        if self.icons:
            res["icons"] = self.icons
        return res


def resource_template_func_result(resource: Union[Resource, ResourceTemplate], params):
    func_result = resource.func(**params)
    if isinstance(func_result, ResourceGetResult):
        func_result.uri = resource.uri
    else:
        if isinstance(func_result, str):
            text = func_result
        else:
            text = json.dumps(func_result)
        func_result = ResourceGetResult(
            uri=resource.uri,
            text=text,
            mimeType=resource.mimeType,
        )
    return func_result.model_dump(exclude_none=True)


# Modifications:
# - Copied without functional changes.
# --- Apache-2.0 licensed code below ---

def build_regex(template: str) -> re.Pattern:
    """Build regex pattern for URI template, handling RFC 6570 syntax.

    Supports:
    - `{var}` - simple path parameter
    - `{var*}` - wildcard path parameter (captures multiple segments)
    - `{?var1,var2}` - query parameters (ignored in path matching)
    """
    # Remove query parameter syntax for path matching
    template_without_query = re.sub(r"\{\?[^}]+\}", "", template)

    parts = re.split(r"(\{[^}]+\})", template_without_query)
    pattern = ""
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            name = part[1:-1]
            if name.endswith("*"):
                name = name[:-1]
                pattern += f"(?P<{name}>.+)"
            else:
                pattern += f"(?P<{name}>[^/]+)"
        else:
            pattern += re.escape(part)
    return re.compile(f"^{pattern}$")


def match_uri_template(uri: str, uri_template: str) -> Optional[dict[str, str]]:
    """Match URI against template and extract both path and query parameters.

    Supports RFC 6570 URI templates:
    - Path params: `{var}`, `{var*}`
    - Query params: `{?var1,var2}`
    """
    # Split URI into path and query parts
    uri_path, _, query_string = uri.partition("?")

    # Match path parameters
    regex = build_regex(uri_template)
    match = regex.match(uri_path)
    if not match:
        return None

    params = {k: unquote(v) for k, v in match.groupdict().items()}

    # Extract query parameters if present in URI and template
    if query_string:
        query_param_names = extract_query_params(uri_template)
        parsed_query = parse_qs(query_string)

        for name in query_param_names:
            if name in parsed_query:
                # Take first value if multiple provided
                params[name] = parsed_query[name][0]  # type: ignore[index]

    return params


def extract_query_params(uri_template: str) -> set[str]:
    """Extract query parameter names from RFC 6570 `{?param1,param2}` syntax."""
    match = re.search(r"\{\?([^}]+)\}", uri_template)
    if match:
        return {p.strip() for p in match.group(1).split(",")}
    return set()
