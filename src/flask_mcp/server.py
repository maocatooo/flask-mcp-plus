import functools
from typing import List, Dict, Any, Callable, Optional, Union

from .handler import Handler
from .streamable_http import _streamable_http_app


class MCP:

    def __init__(self, *args, **kwargs):
        self.handler = Handler()
        self._options = kwargs or {}
        if len(args) == 0:
            app = self._options.pop("app", None)
            if app:
                self.init_app(app, *args, **self._options)
        elif len(args) == 2:
            name, import_name = args
            self._options.update(
                name=name,
                import_name=import_name,
            )
        elif len(args) == 3:
            app, name, import_name = args
            self._options.update(
                name=name,
                import_name=import_name,
            )
            if app:
                self.init_app(app, **self._options)
        else:
            raise ValueError("Invalid arguments must (app, name, import_name) or (name, import_name)")

    def init_app(self, app, name=None, import_name=None, url_prefix="/mcp", version="0.0.1"):
        options = {
            "name": name,
            "import_name": import_name,
            "url_prefix": url_prefix,
            "version": version,
        }
        for k, v in options.items():
            if v is not None:
                self._options.setdefault(k, v)

        self.handler.init(**self._options)
        _streamable_http_app(self, app, **self._options)

    def tool(
            self,
            func_or_name: Optional[Union[Callable, str]] = None,
            *,
            name: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            output_schema: Optional[Dict[str, Any]] = None,
            icons: Optional[List[Dict]] = None,
    ):
        def wraps(fn: Callable):
            self.handler.add_tool_from_func(
                fn,
                name=name,
                title=title,
                description=description,
                output_schema=output_schema,
                icons=icons,
            )
            return fn

        if func_or_name is not None and callable(func_or_name):
            return wraps(func_or_name)
        if isinstance(func_or_name, str):
            name = name or func_or_name
            return wraps
        return wraps

    def resource(self, uri, *,
                 name: Optional[str] = None,
                 mime_type: Optional[str] = None,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 icons: Optional[List[Dict]] = None,
                 ):

        def wraps(func):
            self.handler.add_resource_from_func(func, uri,
                                                name=name,
                                                mime_type=mime_type or "text/plain",
                                                title=title,
                                                description=description,
                                                icons=icons,
                                                )
            return functools.wraps(func)

        return wraps

    def prompt(
            self,
            func_or_name: Optional[Union[Callable, str]] = None,
            *,
            name: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            icons: Optional[List[Dict]] = None,
    ):
        def wraps(fn: Callable):
            self.handler.add_prompt_from_func(
                fn,
                name=name,
                title=title,
                description=description,
                icons=icons,
            )
            return fn

        if func_or_name is not None and callable(func_or_name):
            return wraps(func_or_name)
        if isinstance(func_or_name, str):
            name = name or func_or_name
            return wraps
        return wraps
