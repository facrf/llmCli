"""Minimal MCP stdio server used only by the integration test."""
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if request_id is None:
        continue
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {}}
    elif method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "echo",
                    "description": "Echoes a value",
                    "inputSchema": {"type": "object", "properties": {"value": {"type": "string"}}},
                }
            ]
        }
    elif method == "tools/call":
        value = request.get("params", {}).get("arguments", {}).get("value", "")
        result = {"content": [{"type": "text", "text": value}]}
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
