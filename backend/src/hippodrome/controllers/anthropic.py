from hippodrome.controllers import BaseController
from typing import Any

from pydantic import ConfigDict


class AnthropicController(BaseController):
    """A controller that uses a model served on the Anthropic API to generate responses."""
    model_config = ConfigDict(protected_namespaces=())

    model_name: str = "claude-3-sonnet-20240229"
    """The name of the model to use for generating responses."""
    client: Any
    """The Anthropic client used to generate responses."""

    def __init__(self):
        try:
            from anthropic import Anthropic
            self.client = Anthropic()
        except ImportError:
            raise ImportError("The 'anthropic' package is required to use the AnthropicController, but it is not installed. Please install it using 'pip install anthropic'")

        super().__init__()

    def _generate(self) -> str:
        """Generates a response using the message history"""
        messages = [message.to_compatible() for message in self.messages]

        completion = self.client.messages.create(
            model=self.model_name,
            messages=messages
        )

        return completion.choices[0].message.content
