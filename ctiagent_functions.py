import asyncio
import aiohttp
import html2text
from random import randint
from typing import Annotated
from semantic_kernel.functions import kernel_function

class RandomNumberPlugin:
    """Generates a Random Number"""

    @kernel_function(
      name='gen_random',
      description="Generate a random number given a low and high bound"
    )
    async def gen_random(
      self,
      low: Annotated[int, "Lower bound of the random number"],
      high: Annotated[int, "Upper bound of the random number"]
    ) -> Annotated[int, "Generated random number within the bounds"]:
        print(f"Running gen_random with low={low}, high={high}")
        return randint(low, high)

class WebPlugin:
    """A Plugin to work with Web URLs"""

    @kernel_function(name="download_report", description="Given a URL, convert the page to markdown text and return it as a string")
    async def load_from_web(
        self, url: Annotated[str, "URL to read from the web into markdown content"]
    ) -> Annotated[bytes, "The contents from the site, formatted as Markdown"]:
        async with aiohttp.ClientSession() as session:
            resphtml = await session.get(url)
            async with resphtml:
                resptxt = html2text.html2text(await resphtml.text())
                return resptxt

        return None

class FilePlugin:
    """A Plugin to handle work with files"""

    @kernel_function(
        name="load_text_file_content",
        description="Load a file from disk, given a filename. Returns a bytestring of the file contents."
    )
    async def load_text_file(
        self, file_name: Annotated[str, "The name and path of the file on disk to return the text contents of"]
    ) -> Annotated[bytes, "The contents from the file"]:
        with open(file_name, "rb") as txtfile:
            return txtfile.read()
