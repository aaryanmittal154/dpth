class ToolError(Exception):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message


class DeptheonError(Exception):
    """Base exception for all Deptheon errors"""


class TokenLimitExceeded(DeptheonError):
    """Exception raised when the token limit is exceeded"""
