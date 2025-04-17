import random
import asyncio
from mcp.server.fastmcp import FastMCP
from typing import Annotated

# Construct an MCP Server named FruitMCP
mcp = FastMCP("FruitMCP")

# Declare a tool function named fruit_kind_color that takes a string describing the kind of
# fruit being inquired about, and returns a server-defined color for that fruit
@mcp.tool()
def fruit_kind_color(
    kind: Annotated[str, "The name of the fruit we want to look up the color of"],
) -> Annotated[str, "The color of the fruit named in kind"]:
    """Given a fruit name in kind, if it is known then return its color as a string.
       If unknown, then the tool will return a None response"""
    if kind == "strawberry" or kind == "tomato":
        return "red"
    elif kind == "banana":
        return "yellow"
    elif kind == "mango":
        return "green"

    return None

def main():
    asyncio.run(mcp.run_stdio_async())

if __name__ == "__main__":
    main()
