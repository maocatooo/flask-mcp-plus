import json
from typing import Any, Callable, Optional, Dict

from pydantic import Field, BaseModel

from .types import ToolCallResult, Text, Image, Audio, ResourceLink, EmbeddedResource


class Tool(BaseModel):
    """
    Tool class
    """
    name: str
    func: Callable[..., Any] = Field(exclude=True)
    title: Optional[str] = None
    description: Optional[str] = None
    input_schema: Dict = Field(default_factory=dict)
    output_schema: Optional[Dict] = None
    icons: Optional[list] = None

    def definition(self):
        info: Dict[str, Any] = {
            "name": self.name,
            "inputSchema": self.input_schema,
        }
        if self.title:
            info["title"] = self.title
        if self.icons:
            info["icons"] = self.icons
        if self.output_schema:
            info["outputSchema"] = self.output_schema
        if self.description:
            info["description"] = self.description
        return info


def _is_content(obj):
    return isinstance(obj, (Text, Image, Audio, ResourceLink, EmbeddedResource))


def tool_func_result(tool: Tool, params):
    func_result = tool.func(**params)
    res = ToolCallResult()
    if _is_content(func_result):
        res.content = [func_result]
    elif isinstance(func_result, ToolCallResult):
        res = func_result
    elif isinstance(func_result, (list, dict)):
        if isinstance(func_result, list) and len(func_result) and _is_content(func_result[0]):
            res.content = func_result
        else:
            res.structuredContent = func_result
    else:
        res.content = [Text(text=str(func_result))]
    if res.structuredContent and len(res.content) == 0:
        res.content = [Text(text=json.dumps(res.structuredContent))]
    return res.model_dump(exclude_none=True)
