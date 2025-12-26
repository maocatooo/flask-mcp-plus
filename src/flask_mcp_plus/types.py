from __future__ import annotations

from typing import Optional, Any, Literal, Union, Dict, List

from pydantic import BaseModel, Field


class FieldInfo(BaseModel):
    """Field information description class"""
    description: str = ""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    exclusive_minimum: Optional[float] = None
    exclusive_maximum: Optional[float] = None
    multiple_of: Optional[float] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    unique_items: Optional[bool] = None
    enum: Optional[list] = None
    format: Optional[str] = None
    examples: Optional[list] = None
    default: Any = None
    extra: Optional[dict] = None


class Resource(BaseModel):
    uri: str
    name: str
    mimeType: str = "text/plain"
    title: Optional[str] = None
    description: Optional[str] = None
    icons: Optional[list] = None


class ToolCallResult(BaseModel):
    content: List[Content] = Field(default_factory=list)
    structuredContent: Optional[Dict] = None
    isError: bool = False


class Text(BaseModel):
    type: Literal['text'] = "text"
    text: str


class Image(BaseModel):
    type: Literal['image'] = "image"
    data: str
    mimeType: str = "image/png"


class Audio(BaseModel):
    type: Literal['audio'] = "audio"
    data: str
    mimeType: str = "audio/wav"


class ResourceLink(BaseModel):
    type: Literal['resource'] = "resource_link"
    uri: str
    name: str
    mimeType: str = "text/plain"
    description: Optional[str] = None


class EmbeddedResource(BaseModel):
    type: Literal['resource'] = "resource"
    resource: Resource


class Message(BaseModel):
    role: Literal['user', 'assistant'] = "user"
    content: Union[Text, Image, Audio, EmbeddedResource]


class PromptGetResult(BaseModel):
    description: str = ""
    messages: List[Message] = Field(default_factory=list)


Content = Union[Text, Image, Audio, ResourceLink, EmbeddedResource]


class ResourceGetResult(BaseModel):
    uri: Optional[str] = None
    mimeType: str = "text/plain"
    blob: Optional[str] = None
    text: Optional[str] = None
