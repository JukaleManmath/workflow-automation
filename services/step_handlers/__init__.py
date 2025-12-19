"""
Registry for step handlers.
Maps string step types to StepHandler instances.
"""
from .http_request_handler import HTTPRequestHandler
from .ai_summarize_handler import AISummarizeHandler

HANDLER_REGISTRY = {
    "HTTP_REQUEST": HTTPRequestHandler(),
    "AI_SUMMARIZE": AISummarizeHandler()
}
