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
from autogen_ext.tools.mcp import (
    SseServerParams,
    StreamableHttpServerParams,
    mcp_server_tools,
)
from autogen_ext.memory.canvas import TextCanvasMemory
from openai import RateLimitError

# Import secrets from local_settings.py
import local_settings


# Enumeration of available back-ends
class CTIgorBackend(Enum):
    AZURE_OPENAI = 1
    OLLAMA_LOCAL = 2


class CTIReport(object):
    def __init__(self):
        self.type = "null"

    def summarize_prompt(self) -> str:
        return ""

    def get_path(self):
        return ""


class CTIWebReport(object):
    def __init__(self, url: str):
        self.type = "web"
        self.url = url

    def summarize_prompt(self) -> str:
        return f"Summarize the webpage at {self.url} for me"

    def get_path(self):
        return self.url


class CTIFileReport(object):
    def __init__(self, filename: str):
        self.type = "file"
        self.filename = filename

    def summarize_prompt(self) -> str:
        return f"Summarize the text file {self.filename} for me"

    def get_path(self):
        return self.filename


class CTIgor(object):
    def __init__(
        self,
        backend=CTIgorBackend.AZURE_OPENAI,
        mcp_servers=[],
        report: CTIReport | CTIWebReport | CTIFileReport = CTIReport(),
    ):
        # Define the Azure OpenAI AI Connector and connect to the deployment Terraform provisioned from main.tf
        if backend == CTIgorBackend.AZURE_OPENAI:
            self.chat_service = AzureOpenAIChatCompletionClient(
                azure_deployment=local_settings.deployment,
                api_key=local_settings.azure_api_key,
                azure_endpoint=local_settings.endpoint,
                # api_version="2024-10-21",
                api_version="2025-04-01-preview",
                model="gpt-4.1-nano",
            )
        elif backend == CTIgorBackend.OLLAMA_LOCAL:
            self.chat_service = OllamaChatCompletionClient(
                model="llama3.2:3b",
            )
        else:
            raise ValueError("Invalid LLM backend specified")

        self.mcp_server_urls = mcp_servers

        # Initialize a TextCanvasMemory to maintain text artifacts
        self.canvas = TextCanvasMemory()

        # Initially load the report into the agent's context
        self.report = report

    def get_summary(self) -> str:
        return self.summary

    def get_context_entity(self) -> str:
        return self.report.get_path()

    async def init_agent(self):
        # Initialize the MCP tools
        await self.init_mcp()

        tools = []
        for mcp_tool in self.mcp_tools:
            tools.extend(mcp_tool)

        # Add the TextCanvasMemory tools
        # tools.append(self.canvas.get_apply_patch_tool())
        # tools.append(self.canvas.get_update_file_tool())

        # Instantiate the CTI Agent
        self.agent = AssistantAgent(
            name="ctigor",
            model_client=self.chat_service,
            # Register the tools to use
            tools=tools,
            reflect_on_tool_use=True,
            # Register the memory
            memory=[self.canvas],
        )

        summarize_prompt = self.report.summarize_prompt()
        self.summary = ""
        if summarize_prompt:
            self.summary = await self.prompt(summarize_prompt)

    async def prompt(self, input_prompt: str):
        # Prompt the model with the given input + state, waiting for response
        response = None
        while response is None:
            try:
                response = await self.agent.on_messages(
                    [TextMessage(content=input_prompt, source="user")],
                    CancellationToken(),
                )
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
            StreamableHttpServerParams(url=u) for u in self.mcp_server_urls
        ]
        self.mcp_tools = [await mcp_server_tools(x) for x in self.octi_mcp_params]
