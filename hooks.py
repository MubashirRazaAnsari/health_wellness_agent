from typing import Any, Dict, Optional
from context import UserSessionContext

class RunHooks:
    """Global run hooks for tracking agent and tool lifecycle events."""

    @staticmethod
    async def on_agent_start(context: UserSessionContext) -> None:
        """Called when an agent starts processing a request."""
        print(f"Agent started processing request for user {context.name}")

    @staticmethod
    async def on_agent_end(context: UserSessionContext, response: Dict[str, Any]) -> None:
        """Called when an agent finishes processing a request."""
        print(f"Agent finished processing request for user {context.name}")
        print(f"Response: {response}")

    @staticmethod
    async def on_tool_start(context: UserSessionContext, tool_name: str) -> None:
        """Called when a tool starts executing."""
        print(f"Tool {tool_name} started for user {context.name}")

    @staticmethod
    async def on_tool_end(context: UserSessionContext, tool_name: str, result: Any) -> None:
        """Called when a tool finishes executing."""
        print(f"Tool {tool_name} finished for user {context.name}")
        print(f"Result: {result}")

    @staticmethod
    async def on_handoff(context: UserSessionContext, from_agent: str, to_agent: str) -> None:
        """Called when control is handed off between agents."""
        print(f"Handoff from {from_agent} to {to_agent} for user {context.name}")
        context.log_handoff(f"Handoff from {from_agent} to {to_agent}")

class AgentHooks:
    """Agent-specific hooks for tracking lifecycle events."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    async def on_start(self, context: UserSessionContext) -> None:
        """Called when this agent starts processing."""
        print(f"{self.agent_name} started processing")

    async def on_end(self, context: UserSessionContext, response: Dict[str, Any]) -> None:
        """Called when this agent finishes processing."""
        print(f"{self.agent_name} finished processing")

    async def on_tool_start(self, context: UserSessionContext, tool_name: str) -> None:
        """Called when this agent starts using a tool."""
        print(f"{self.agent_name} started using tool {tool_name}")

    async def on_tool_end(self, context: UserSessionContext, tool_name: str, result: Any) -> None:
        """Called when this agent finishes using a tool."""
        print(f"{self.agent_name} finished using tool {tool_name}")

    async def on_handoff(self, context: UserSessionContext, to_agent: str) -> None:
        """Called when this agent hands off control."""
        print(f"{self.agent_name} handing off to {to_agent}")
        context.log_handoff(f"{self.agent_name} handed off to {to_agent}") 