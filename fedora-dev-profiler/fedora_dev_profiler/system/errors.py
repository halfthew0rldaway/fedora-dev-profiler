"""
Defines common error structures to pass diagnostic warnings up to the UI.
"""
from dataclasses import dataclass

@dataclass
class ErrorData:
    subsystem: str
    message: str
    is_critical: bool = False
