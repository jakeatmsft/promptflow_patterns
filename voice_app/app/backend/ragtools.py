import re
from typing import Any
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
from promptflow.client import load_flow
from promptflow.tracing import start_trace, trace

_analyst_tool_schema = {
    "type": "function",
    "name": "analyst_tool",
    "description": "Tool for performing mathematical and statistical analysis on general data on the web.  The analyst tool can perform search and analysis of data on the web",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "analysis task"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

@trace
async def _analyst_tool(args: Any) -> ToolResult:
    print(f"Performing '{args['query']}' .")
    f = load_flow("./semantic_kernel_autogen_planner")
    start_trace()
    result = f(chat_history=[],question=args['query'])
    return ToolResult(result, ToolResultDirection.TO_SERVER)

KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_=\-]+$')

def attach_rag_tools(rtmt: RTMiddleTier, credentials: AzureKeyCredential | DefaultAzureCredential) -> None:
    rtmt.tools["analyst_tool"] = Tool(schema=_analyst_tool_schema, target=lambda args: _analyst_tool(args))