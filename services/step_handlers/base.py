"""
Base interface for all workflow step handlers.
Each handler knows how to execute a specific step type (HTTP, AI, DELAY, etc.).
"""
from typing import Dict, Any

class StepHandler:
    """
        All step handlers implement run(step, context) and return a dict:
        {
        "status" : "SUCCESS" | "FAILED"
        "output" : {}
        "error" : {}
        "context_patch" : {}
        }
    """

    async def run(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Each handler must implement run()")
