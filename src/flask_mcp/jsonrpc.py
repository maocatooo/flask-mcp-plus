def jsonrpc_result(req_id, result: dict):
    """Build a JSON-RPC success response."""
    res = {"jsonrpc": "2.0", "id": req_id, "result": result}
    return res


def jsonrpc_error(req_id, message: str, code: int = -32600):
    """Build a JSON-RPC error response."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
