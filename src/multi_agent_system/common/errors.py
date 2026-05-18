class MultiAgentSystemError(RuntimeError):
    """Base error for application-level failures."""


class A2AClientError(MultiAgentSystemError):
    """Raised when an A2A service request fails."""


class MCPToolError(MultiAgentSystemError):
    """Raised when an MCP tool call fails."""