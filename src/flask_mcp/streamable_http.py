import json
from logging import getLogger
from typing import Iterable, Any, Generator

from flask import Flask, Blueprint, request, Response, stream_with_context

from .handler import Handler
from .jsonrpc import jsonrpc_result, jsonrpc_error

logger = getLogger(__name__)
PROTOCOL_VERSION = "2025-06-18"


def generate_response(response: Iterable[Any]):
    def parse_response(data: Any) -> str:
        _data = ""
        if isinstance(data, str):
            _data = data
        else:
            _data = json.dumps(data)
        return f"data: {_data} \n\n"

    def generate() -> Generator:
        for data in response:
            yield parse_response(data)

    return Response(stream_with_context(generate()), status=200, mimetype="text/event-stream")


class StreamableHttp:
    def __init__(self, handler: Handler):
        self.handler = handler

    def notifications_initialized(self, req_id, params):
        return jsonrpc_result(req_id, {})

    def initialize(self, req_id, params):
        return jsonrpc_result(req_id, self.handler.initialize())

    def tools_list(self, req_id, params):
        return jsonrpc_result(req_id, self.handler.tool_list())

    def tools_call(self, req_id, params):
        name = params.get("name")
        arguments = params.get("arguments", {})
        return jsonrpc_result(req_id, self.handler.tool_call(name, arguments))

    def prompts_list(self, req_id, params):
        return jsonrpc_result(req_id, self.handler.prompts_list())

    def resources_list(self, req_id, params):
        return jsonrpc_result(req_id, self.handler.resources_list())

    def resources_read(self, req_id, params):
        return jsonrpc_result(req_id, self.handler.resources_read(params["uri"]))

    def resources_templates_list(self, req_id, params):
        return jsonrpc_result(req_id, self.handler.resources_templates_list())

    def prompts_get(self, req_id, params):
        name = params.get("name")
        arguments = params.get("arguments", {})
        return jsonrpc_result(req_id, self.handler.prompts_get(name, arguments))

    def _method(self):
        data = request.get_json()
        md = data.get("method")
        req_id = data.get("id")
        params = data.get("params", {})
        logger.debug(f"MCP request: {md} (id={req_id},  params={params})")
        if md == "tools/call":
            return self.tools_call(req_id, params)
        if md == "resources/read":
            return self.resources_read(req_id, params)
        elif md == "tools/list":
            return self.tools_list(req_id, params)
        elif md == "resources/list":
            return self.resources_list(req_id, params)
        elif md == "resources/templates/list":
            return self.resources_templates_list(req_id, params)
        elif md == "prompts/list":
            return self.prompts_list(req_id, params)
        elif md == "prompts/get":
            return self.prompts_get(req_id, params)
        elif md == "initialize":
            return self.initialize(req_id, params)
        elif md == "notifications/initialized":
            return self.notifications_initialized(req_id, params)
        return jsonrpc_error(req_id, "Method not found")

    def method(self):
        """
        Handle MCP request
        """
        res = self._method()
        return generate_response([res])


def _streamable_http_app(mcp, app: Flask, name, import_name, url_prefix="/mcp", **kwargs):
    handler: Handler = mcp.handler
    mcp_bp = Blueprint(name, import_name)
    mcp_bp.add_url_rule('', None, methods=["POST"], view_func=StreamableHttp(handler).method)
    app.register_blueprint(mcp_bp, url_prefix=url_prefix)
