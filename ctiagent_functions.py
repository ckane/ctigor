import asyncio
import aiohttp
import html2text
from random import randint
from typing import Annotated

async def gen_random(
  low: Annotated[int, "Lower bound of the random number"],
  high: Annotated[int, "Upper bound of the random number"]
) -> Annotated[int, "Generated random number within the bounds"]:
    """Generate a random number given a low and high bound"""
    print(f"Running gen_random with low={low}, high={high}")
    return randint(low, high)

async def load_from_web(
    url: Annotated[str, "URL to read from the web into markdown content"]
) -> Annotated[bytes, "The contents from the site, formatted as Markdown"]:
    """Given a URL, convert the page to markdown text and return it as a string"""
    async with aiohttp.ClientSession() as session:
        resphtml = await session.get(url)
        async with resphtml:
            resptxt = html2text.html2text(await resphtml.text())
            return resptxt

    return None

async def load_text_file(
    file_name: Annotated[str, "The name and path of the file on disk to return the text contents of"]
) -> Annotated[bytes, "The contents from the file"]:
    """Load a file from disk, given a filename. Returns a bytestring of the file contents."""
    with open(file_name, "rb") as txtfile:
        return txtfile.read()
