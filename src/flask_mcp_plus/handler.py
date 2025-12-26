import inspect
from typing import Optional, List, Dict, Any

from .json_schema import func_to_json_schema, func_to_arguments
from .prompt import Prompt, prompt_func_result
from .resource import Resource, ResourceTemplate, match_uri_template, resource_func_result, \
    resource_template_func_result
from .tool import Tool, tool_func_result

PROTOCOL_VERSION = "2025-06-18"


class Handler:
    """
    Handler class
    """

    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self.resources: dict[str, Resource] = {}
        self.resource_templates: dict[str, ResourceTemplate] = {}
        self.prompts: dict[str, Prompt] = {}
        self.name = None
        self.version = None

    def init(self, name="mcp", version="0.0.1", **kwargs):
        self.name = name
        self.version = version

    def add_tool_from_func(self, func,
                           name: Optional[str] = None,
                           title: Optional[str] = None,
                           description: Optional[str] = None,
                           output_schema: Optional[Dict[str, Any]] = None,
                           icons: Optional[List[Dict]] = None, ):
        json_schema = func_to_json_schema(func)
        if name is None:
            name = func.__name__
        if description is None:
            description = inspect.getdoc(func)
        tool = Tool(
            name=name,
            title=title,
            output_schema=output_schema,
            description=description,
            func=func,
            input_schema=json_schema,
            icons=icons,
        )
        self.add_tool(tool)

    def add_resource_from_func(self, func, uri,
                               *,
                               name: Optional[str] = None,
                               title: Optional[str] = None,
                               mime_type: Optional[str] = None,
                               description: Optional[str] = None,
                               icons: Optional[List[Dict]] = None,
                               ):
        if name is None:
            name = func.__name__
        if description is None:
            description = inspect.getdoc(func)

        has_uri_params = "{" in uri and "}" in uri
        if has_uri_params:
            self.add_resource_template_from_func(func, uri,
                                                 name=name,
                                                 title=title,
                                                 mime_type=mime_type,
                                                 description=description,
                                                 icons=icons,
                                                 )
        else:
            resource = Resource(
                func=func,
                uri=uri,
                name=name,
                title=title,
                mimeType=mime_type,
                description=description,
                icons=icons,
                arguments=func_to_arguments(func),
            )
            self.add_resource(resource)

    def add_resource_template_from_func(self, func, uri,
                                        *,
                                        name: Optional[str] = None,
                                        title: Optional[str] = None,
                                        mime_type: Optional[str] = None,
                                        description: Optional[str] = None,
                                        icons: Optional[List[Dict]] = None,
                                        ):

        resource = ResourceTemplate(
            uri=uri,
            name=name,
            title=title,
            mimeType=mime_type,
            description=description,
            func=func,
            icons=icons,
            arguments=func_to_arguments(func)
        )
        self.add_resource_template(resource)

    def add_prompt_from_func(self, func,
                             name: Optional[str] = None,
                             title: Optional[str] = None,
                             description: Optional[str] = None,
                             icons: Optional[List[Dict]] = None, ):
        arguments = func_to_arguments(func)
        if name is None:
            name = func.__name__
        if description is None:
            description = inspect.getdoc(func)
        tool = Prompt(
            name=name,
            title=title,
            description=description,
            func=func,
            arguments=arguments,
            icons=icons,
        )
        self.add_prompt(tool)

    def add_tool(self, tool):
        if tool.name in self.tools:
            raise Exception(f"Tool {tool.name} already exists")
        self.tools[tool.name] = tool

    def add_resource(self, resource: Resource):
        if resource.uri in self.resources:
            raise Exception(f"Resource {resource.uri} already exists")
        self.resources[resource.uri] = resource

    def add_resource_template(self, resource):
        if resource.uri in self.resource_templates:
            raise Exception(f"Resource template {resource.uri} already exists")
        self.resource_templates[resource.uri] = resource

    def add_prompt(self, prompt):

        if prompt.name in self.prompts:
            raise Exception(f"Prompt {prompt.name} already exists")
        self.prompts[prompt.name] = prompt

    def tool_list(self):
        return {"tools": [item.definition() for item in self.tools.values()]}

    def resources_list(self):
        return {"resources": [item.definition() for item in self.resources.values()]}

    def resources_templates_list(self):
        return {"resourceTemplates": [item.definition() for item in self.resource_templates.values()]}

    def prompts_list(self):
        return {"prompts": [item.definition() for item in self.prompts.values()]}

    def tool_call(self, name, arguments):
        if tool := self.get_tool(name):
            return tool_func_result(tool, arguments)
        raise Exception(f"Tool {name} not found")

    def resources_read(self, uri):
        if resource := self.get_resource(uri):
            return {"contents": [
                resource_func_result(resource)
            ]}

        for resource_template_uri, resource_template in self.resource_templates.items():
            params = match_uri_template(uri, resource_template_uri)
            if params is not None:
                if not all(params.get(arg["name"]) for arg in resource_template.arguments if arg.get("required")):
                    continue
                return {"contents": [
                    resource_template_func_result(resource_template, params)
                ]}

        raise Exception(f"Resource {uri} not found")

    def prompts_get(self, name, arguments):
        if prompt := self.get_prompt(name):
            if not all(arguments.get(arg["name"]) for arg in prompt.arguments if arg.get("required")):
                raise Exception(f"Prompt {name} missing required arguments")
            return prompt_func_result(prompt, arguments)
        raise Exception(f"Prompt {name} not found")

    def get_tool(self, name):
        return self.tools.get(name)

    def get_resource(self, uri):
        return self.resources.get(uri)

    def get_prompt(self, name) -> Optional[Prompt]:
        return self.prompts.get(name)

    def initialize(self):
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {
                "tools": {"listChanged": False},
                "prompts": {},
                "resources": {},
                # "completions": {}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version,
            },
        }
