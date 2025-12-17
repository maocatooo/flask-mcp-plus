# Flask-MCP

Flask integration for Model Context Protocol (MCP) - a framework for building MCP servers with Flask.

[![License: apache-2-0](https://img.shields.io/badge/License-Apache2.0-yellow.svg)](https://opensource.org/licenses/apache-2-0)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-%3E%3D3.0-orange)](https://flask.palletsprojects.com/)

## Overview

Flask-MCP provides a simple and intuitive way to create Model Context Protocol (MCP) servers using Flask. It allows
developers to easily expose tools, resources, and prompts that can be consumed by MCP clients, facilitating rich
interactions between language models and external systems.

## Features

- **Easy Integration**: Seamless integration with Flask applications
- **Type Safety**: Built-in support for type hints and Pydantic validation
- **Tool Support**: Define MCP tools with automatic schema generation
- **Resource Management**: Handle static and dynamic resources with URI templates
- **Prompt Generation**: Create dynamic prompts for AI models
- **JSON Schema Generation**: Automatic generation of JSON schemas from Python functions
- **Streaming Support**: Streamable HTTP responses for large data

## Installation

```bash
pip install flask-mcp-core
```

## Quick Start

Here's a basic example to get you started:

```python
from flask import Flask
from flask_mcp import MCP

app = Flask(__name__)
mcp = MCP()
mcp.init_app(app, "my_mcp_server", __name__)


# Define a simple tool
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


# Define a resource
@mcp.resource("http://example.com/data.json")
def get_data():
    """Return some static data."""
    return {"message": "Hello, MCP!"}


# Define a prompt
@mcp.prompt
def greeting(name: str) -> str:
    """Create a personalized greeting."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    app.run(debug=True)
```

## Core Concepts

### Tools

Tools are functions that can be called by MCP clients. They can accept parameters and return structured results.

```python
from flask_mcp import Text, Field
from typing import Annotated


@mcp.tool(
    name="calculate_sum",
    title="Calculate Sum",
    description="Add two floating point numbers",
    icons=[
        {
            "src": "https://example.com/calculator-icon.png",
            "mimeType": "image/png",
            "sizes": ["48x48"]
        }
    ]
)
def add_float(a: Annotated[float, Field(description="The first number")],
              b: Annotated[float, Field(description="The second number")]) -> Text:
    return Text(text=str(a + b))
```

### Resources

Resources provide data that can be fetched by URI. Flask-MCP supports both static URIs and dynamic URI templates with
parameters.

```python
@mcp.resource("file://data/config.json")
def get_config():
    """Return static configuration data."""
    return {"setting1": "value1", "setting2": "value2"}


# Dynamic resource with path parameters
@mcp.resource("file://data/users/{user_id}.json")
def get_user(user_id: str):
    """Return user data by ID."""
    return {"id": user_id, "name": f"User {user_id}"}
```

### Prompts

Prompts are specialized functions that return structured content to guide AI models.

```python
from flask_mcp import Message, Text


@mcp.prompt
def daily_fact() -> Message:
    """Return a daily fact as a message."""
    return Message(
        content=Text(text="The capital of France is Paris.")
    )
```

## Advanced Usage

### Custom Output Schema

For tools that return structured data, you can specify a custom JSON schema:

```python
@mcp.tool(
    output_schema={
        "type": "object",
        "properties": {
            "result": {"type": "string"},
            "success": {"type": "boolean"}
        },
        "required": ["result", "success"]
    }
)
def api_call():
    return {
        "result": "Operation completed successfully",
        "success": True
    }
```

### Multiple Content Types

Tools can return multiple content types in a single response:

```python
from flask_mcp import Image, Text


@mcp.tool
def multi_data():
    return [
        Image(data=base64_image_data),
        Text(text="Here's an image and some text")
    ]
```

## Running the Examples

The repository includes comprehensive examples in the `src/example/` directory:

- `tools.py` - Examples of various tool definitions
- `resources.py` - Examples of resource handling
- `prompt.py` - Examples of prompt creation

To run an example:

```bash
cd src/example
python tools.py
```

## Configuration

The MCP server can be configured with various options:

```python
mcp = MCP()
mcp.init_app(
    app,
    name="my-awesome-server",
    import_name=__name__,
    url_prefix="/mcp",  # Endpoint prefix for MCP routes
    version="1.0.0"
)
```

## API Endpoints

Once configured, Flask-MCP automatically creates the following endpoints:

- `POST /mcp` - Main MCP JSON-RPC endpoint
- `GET /mcp/health` - Health check endpoint

## Development

### Prerequisites

- Python 3.9+
- Flask 3+
- Pydantic 2+

### Setup

```bash
# Clone the repository
git clone https://github.com/flask-mcp/flask-mcp.git
cd flask-mcp

# Install dependencies
uv sync

```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/) - The official MCP specification
- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [Pydantic](https://pydantic.dev/) - Data validation library
- [fastmcp](https://github.com/jlowin/fastmcp) - A high-performance MCP implementation

## Support

If you encounter any issues or have questions, please file an issue on
the [GitHub repository](https://github.com/flask-mcp/flask-mcp/issues).