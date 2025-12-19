from services.step_handlers.base import StepHandler
from typing import Dict, Any
import ollama

class AISummarizeHandler(StepHandler):
    async def run(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        cfg = step.config or {}

        # which context key to summarize
        source_key = cfg.get("source_key") or "http_response"
        save_as = cfg.get("save_as") or "summary"
        model = "llama3"

        # resolve input text
        source_val = context[source_key]["data"]["body"]
        if source_val is None:
            return {
                "status": "FAILED",
                "output": None,
                "error": {"message": f"Missing context key to summarize: {source_key}"},
                "context_patch": {}
            }
        
        text = source_val if isinstance(source_val, str) else str(source_val)

        try:
            prompt = f"""
            Please provide a concise and detailed summary of the following document. 
            Focus on the key points, main ideas, and any action items.
            
            Document Content:
            ---
            {text}
            ---

            Summary:
            """
            model = "llama3"
            # Send the request to Ollama
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are an expert summarizer. Your goal is to condense the provided text into a clear and comprehensive summary.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )

            summary = response["message"]["content"]

            return {
                "status": "SUCCESS",
                "output": {"summary": summary},
                "error": None,
                "context_patch": {save_as: summary},
            }

        except Exception as e:
            return {
                "status": "FAILED",
                "output": None,
                "error": {"message": str(e)},
                "context_patch": {}
            }