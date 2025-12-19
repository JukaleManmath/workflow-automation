import httpx
from services.step_handlers.base import StepHandler
from typing import Dict, Any

class HTTPRequestHandler(StepHandler):
    async def run(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        cfg = step.config or {}

        url = cfg.get("url")
        if not url:
            return {
                "status": "FAILED",
                "output": None,
                "error" : {"message": "Missing required config field: url"},
                "context_patch": []
            }
        method = cfg.get("method", "GET").upper()
        headers = cfg.get("headers") or {}
        body = cfg.get("json") or cfg.get("body") or None
        timeout= cfg.get("timeout", 20)
        
        try:

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method=method,url=url, headers=headers, json=body)

            try:
                data = response.json()
            except Exception:
                data = {"text": response.text}
            
            ok = 200 <= response.status_code < 300

            return {
                "status": "SUCCESS" if ok else "FAILED",
                "output": {"status_code": response.status_code, "data": data},
                "context_patch" : {cfg.get("save_as", "http_response"): {"status_code": response.status_code, "data": data} },
                "error": None if ok else {"status_code": response.status_code, "data":data}
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "output": None,
                "error": {"message": str(e)},
                "context_patch": {}
            }