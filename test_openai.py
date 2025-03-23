import asyncio

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from semantic_kernel.kernel import Kernel

from ctiagent import CTIgor

async def main():
    ctigor = CTIgor()
    response = await ctigor.prompt("Tell me a fact about hedgehogs")

    # Display response on console
    print(f"=======\n{response}\n=======")

if __name__ == "__main__":
    asyncio.run(main())
