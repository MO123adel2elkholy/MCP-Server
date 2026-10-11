"""
Simple MCP server that returns usernames from a predefined list.

This module exposes two tools for username selection:
- get_username_random: choose a random username from a user-provided list or the default list
- list_available_usernames: return the default username list with its total count

The tool docstrings are written to be understandable by LLMs and MCP clients.
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
    """
    Return a random username from a provided list or the default built-in list.

    Use this tool when a caller needs a random username without manually managing the source list.
    The tool validates the input and raises clear exceptions if the input is invalid.

    Args:
        user_list (list[str] | None): Optional list of usernames to choose from.
            If omitted or set to None, the built-in USERNAMES list is used.

    Returns:
        str: A success message containing the randomly selected username.

    Raises:
        TypeError: Raised when user_list is not a list or None.
        ValueError: Raised when user_list is an empty list.

    Example:
        get_username_random()
        get_username_random(["alice", "bob", "charlie"])
    """
    try:
        if user_list is not None:
            if not isinstance(user_list, list):
                raise TypeError(
                    f"user_list must be a list or None, got {type(user_list).__name__}"
                )

            if len(user_list) == 0:
                raise ValueError(
                    "Provided user_list is empty. Cannot select a random username."
                )

            selected_list = user_list
        else:
            selected_list = USERNAMES

        selected_username = random.choice(selected_list)
        return f"Successfully retrieved random username: {selected_username}"

    except (TypeError, ValueError):
        raise
    except Exception as exc:
        raise RuntimeError(f"Unexpected error while selecting a username: {exc}") from exc


@mcp.tool()
def list_available_usernames() -> str:
    """
    Return the full list of default usernames available in this server.

    Use this tool to inspect all usernames currently available before choosing one
    or to present the available options to a caller.

    Returns:
        str: A multi-line string containing the usernames and the total count.

    Raises:
        RuntimeError: Raised if the username list cannot be read or formatted.

    Example:
        list_available_usernames()
    """
    try:
        usernames_str = "\n".join([f"- {name}" for name in USERNAMES])
        return f"Available usernames ({len(USERNAMES)} total):\n{usernames_str}"

    except Exception as exc:
        raise RuntimeError(f"Failed to list usernames: {exc}") from exc


if __name__ == "__main__":
    """
    Run the MCP server when this file is executed directly.

    This allows the server to be started as a local stdio MCP process for VS Code
    or other MCP-compatible clients.
    """
    mcp.run()