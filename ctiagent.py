import asyncio

from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from semantic_kernel.kernel import Kernel

from ctiagent_functions import RandomNumberPlugin, FilePlugin, WebPlugin

# Import secrets from local_settings.py
import local_settings

class CTIgor(object):
    def __init__(self):
        # Initialize a new Kernel to work with
        self.kernel = Kernel()

        # Define the Azure OpenAI AI Connector and connect to the deployment Terraform provisioned from main.tf
        self.chat_service = AzureChatCompletion(
            deployment_name=local_settings.deployment,
            api_key=local_settings.azure_api_key,
            endpoint=local_settings.endpoint,
        )

        # Define a ChatHistory object
        self.chat_history = ChatHistory()

        # Define the request settings to use model defaults
        self.request_settings = AzureChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())

        # Register the RandomNumberPlugin, FilePlugin, WebPlugin with the kernel
        self.kernel.add_plugin(RandomNumberPlugin(), plugin_name="random_number")
        self.kernel.add_plugin(FilePlugin(), plugin_name="file")
        self.kernel.add_plugin(WebPlugin(), plugin_name="web")

    async def prompt(self, input_prompt: str):
        self.chat_history.add_user_message(input_prompt)

        # Prompt the model with the given chat history, waiting for response
        response = await self.chat_service.get_chat_message_content(
            chat_history=self.chat_history, settings=self.request_settings, kernel=self.kernel
        )

        # Ensure response isn't None
        assert response is not None

        # Append the response to the chat_history
        self.chat_history.add_assistant_message(response.content)

        return response
