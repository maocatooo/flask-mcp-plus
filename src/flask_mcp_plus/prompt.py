from typing import Any, Callable, Optional

from pydantic import BaseModel, Field

from .types import PromptGetResult, Message, Text


class Prompt(BaseModel):
    """
    Prompt class
    """
    name: str
    func: Callable[..., Any] = Field(exclude=True)
    title: Optional[str] = None
    description: Optional[str] = None
    arguments: Optional[list] = None
    icons: Optional[list] = None

    def definition(self):
        info: dict[str, Any] = {
            "name": self.name,
            "arguments": self.arguments,
        }
        if self.title:
            info["title"] = self.title
        if self.icons:
            info["icons"] = self.icons
        if self.description:
            info["description"] = self.description
        return info


def prompt_func_result(prompt, arguments):
    messages = prompt.func(**arguments)
    info = PromptGetResult()
    if isinstance(messages, (str, int, float)):
        messages = [
            Message(
                role="assistant",
                content=Text(text=str(messages)),
            )
        ]
        info.messages = messages
    elif isinstance(messages, Message):
        info.description = prompt.description
        info.messages = [messages]
    elif isinstance(messages, PromptGetResult):
        info = messages
        info.description = prompt.description
    else:
        info = PromptGetResult(messages=messages)
    return info.model_dump(exclude_none=True)
