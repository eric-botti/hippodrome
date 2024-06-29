from hippodrome.controllers import BaseController

from typing import Any
from pydantic import ConfigDict


class OllamaController(BaseController):
    """A controller that uses a model served on the Anthropic API to generate responses."""
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    """The name of the model to use for generating responses."""
    client: Any
    """The client used to generate responses."""

    def __init__(self):
        try:
            from ollama import Client
            self.client = Client()
        except ImportError:
            raise ImportError("The 'ollama' package is required to use the OllamaController, but it is not installed. Please install it using 'pip install ollama'")

        super().__init__()

    def _generate(self) -> str:
        """Generates a response using the message history"""
        messages = [message.to_compatible() for message in self.messages]

        response = self.client.chat(
            model=self.model_name,
            messages=messages
        )

        return response["message"]["content"]
