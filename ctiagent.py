import asyncio
import time
from enum import Enum

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console as AgentConsole
from autogen_core.tools import FunctionTool
from autogen_core import CancellationToken
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from openai import RateLimitError

from ctiagent_functions import gen_random, load_from_web, load_text_file

# Import secrets from local_settings.py
import local_settings

# Enumeration of available back-ends
class CTIgorBackend(Enum):
    AZURE_OPENAI = 1
    OLLAMA_LOCAL = 2

class CTIgor(object):
    def __init__(self, backend=CTIgorBackend.AZURE_OPENAI, mcp_servers=[]):
        # Define the Azure OpenAI AI Connector and connect to the deployment Terraform provisioned from main.tf
        if backend == CTIgorBackend.AZURE_OPENAI:
            self.chat_service = AzureOpenAIChatCompletionClient(
                azure_deployment=local_settings.deployment,
                api_key=local_settings.azure_api_key,
                azure_endpoint=local_settings.endpoint,
                api_version="2024-10-21",
                model='gpt-4o-mini',
            )
        elif backend == CTIgorBackend.OLLAMA_LOCAL:
            self.chat_service = OllamaChatCompletionClient(
                model='llama3.2:3b',
            )
        else:
            raise ValueError('Invalid LLM backend specified')

        self.mcp_server_urls = mcp_servers

    async def init_agent(self):
        # Initialize the MCP tools
        await self.init_mcp()

        tools=[gen_random, load_from_web, load_text_file]
        for mcp_tool in self.mcp_tools:
            tools.extend(mcp_tool)

        # Instantiate the CTI Agent
        self.agent = AssistantAgent(
            name="ctigor",
            model_client=self.chat_service,

            # Register the tools to use
            tools=tools,
            reflect_on_tool_use=True,
        )

    async def prompt(self, input_prompt: str):
        # Prompt the model with the given input + state, waiting for response
        response = None
        while response == None:
            try:
                response = await self.agent.on_messages([TextMessage(content=input_prompt, source="user")], CancellationToken())
            except RateLimitError:
                print("Encountered RateLimitError, waiting 90s")
                time.sleep(90)
                response = None

        # Ensure response isn't None
        assert response is not None

        # Strip the ending TERMINATE message that's part of AutoGen's internals
        text_response = response.chat_message.content
        if text_response[-9:] == "TERMINATE":
            text_response = text_response[:-9]

        return text_response

    async def init_mcp(self):
        self.octi_mcp_params = [
            SseServerParams(
                url=u
            ) for u in self.mcp_server_urls
        ]
        self.mcp_tools = [await mcp_server_tools(x) for x in self.octi_mcp_params]
