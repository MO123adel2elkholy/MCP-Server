"""
MCP Server for managing and retrieving usernames.
"""

import random
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("username-server")

USERNAMES = [
    "alice_wonder",
    "bob_builder",
    "charlie_brown",
    "diana_prince",
    "eve_anderson",
    "frank_ocean",
    "grace_hopper",
    "henry_ford",
    "iris_west",
    "jack_sparrow",
]


@mcp.tool()
def get_username_random(user_list: list[str] | None = None) -> str:
    if user_list is not None:
        if not isinstance(user_list, list):
            raise TypeError(f"user_list must be a list or None, got {type(user_list).__name__}")
        if len(user_list) == 0:
            raise ValueError("Provided user_list is empty. Cannot select a random username.")
        selected_list = user_list
    else:
        selected_list = USERNAMES

    return f"Successfully retrieved random username: {random.choice(selected_list)}"


@mcp.tool()
def list_available_usernames() -> str:
    usernames_str = "\n".join([f"- {name}" for name in USERNAMES])
    return f"Available usernames ({len(USERNAMES)} total):\n{usernames_str}"


if __name__ == "__main__":
    mcp.run()
