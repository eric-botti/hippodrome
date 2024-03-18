from controllers.base import BaseController

from typing import Any

from anthropic import Anthropic
from pydantic import Field, ConfigDict


class AnthropicController(BaseController):
    """A controller that models served on the Anthropic API to generate responses."""
    model_config = ConfigDict(protected_namespaces=())

    model_name: str = "gpt-3.5-turbo"
    """The name of the model to use for generating responses."""
    client: Any = Field(default_factory=Anthropic, exclude=True)
    """The OpenAI client used to generate responses."""

    def _generate(self) -> str:
        """Generates a response using the message history"""
        messages = [message.to_compatible() for message in self.messages]

        completion = self.client.messages.create(
            model=self.model_name,
            messages=messages
        )

        return completion.choices[0].message.content
