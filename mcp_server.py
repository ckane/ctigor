import asyncio
import aiohttp
import html2text
import logging
from argparse import ArgumentParser
from fastmcp import FastMCP
from random import randint
from typing import Annotated

# Construct an MCP Server named CTI.MCP
ap = ArgumentParser(description="Execute the CTIgor Supplemental MCP Server")
ap.add_argument(
    "-p",
    "--port",
    required=False,
    type=int,
    default=8001,
    help="TCP port to listen on (default 8001)",
)
ap.add_argument(
    "-s",
    "--sse",
    required=False,
    default=False,
    action="store_true",
    help="Start an SSE server (default: off)",
)
args = ap.parse_args()
log = logging.getLogger(name="CTI.MCP")
log.setLevel("INFO")
mcp = FastMCP(name="CTI.MCP")


@mcp.tool()
async def gen_random(
    low: Annotated[int, "Lower bound of the random number"],
    high: Annotated[int, "Upper bound of the random number"],
) -> Annotated[int, "Generated random number within the bounds"]:
    """Generate a random number given a low and high bound"""
    print(f"Running gen_random with low={low}, high={high}")
    return randint(low, high)


@mcp.tool()
async def load_from_web(
    url: Annotated[str, "URL to read from the web into markdown content"],
) -> Annotated[str, "The contents from the site, formatted as Markdown"]:
    """Given a URL, convert the page to markdown text and return it as a string"""
    async with aiohttp.ClientSession() as session:
        log.info(f"Fetching url: {url}")
        resphtml = await session.get(url)
        async with resphtml:
            resptxt = html2text.html2text(await resphtml.text())
            return resptxt


@mcp.tool()
async def load_text_file(
    file_name: Annotated[
        str, "The name and path of the file on disk to return the text contents of"
    ],
) -> Annotated[bytes, "The contents from the file"]:
    """Load a file from disk, given a filename. Returns a bytestring of the file contents."""
    with open(file_name, "rb") as txtfile:
        return txtfile.read()


def main():
    if args.sse:
        asyncio.run(mcp.run_http_async(port=args.port))
    else:
        asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
