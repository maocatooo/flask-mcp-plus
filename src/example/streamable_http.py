from flask import Flask

from flask_mcp_plus import MCP

app = Flask(__name__)
# mcp = MCP(app, "mcp_server_name", __name__)
"""
mcp = MCP("mcp_server_name", __name__)
mcp.init_app(app)
"""
mcp = MCP()
mcp.init_app(app, "mcp_server_name", __name__)


@mcp.tool
def hello_world():
    """hello world"""
    return "Hello, World!"


@mcp.tool
def add(a: int, b: int):
    """add"""
    return a + b


@mcp.resource("file://a.txt")
def atxt() -> str:
    """get text atxt"""
    return "hello world"


@mcp.prompt
def prompt(text: str) -> str:
    """Simple prompt that returns the input text"""
    return text


if __name__ == "__main__":
    app.run(debug=True)
