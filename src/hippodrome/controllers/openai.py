from hippodrome.controllers import BaseController

from typing import Any

from openai import OpenAI
from pydantic import Field, ConfigDict


class OpenAIController(BaseController):
    """A controller that uses the OpenAI API (or compatible 3rd parties) to generate responses."""
    model_config = ConfigDict(protected_namespaces=())

    model_name: str = "gpt-3.5-turbo"
    """The name of the model to use for generating responses."""
    client: Any = Field(default_factory=OpenAI, exclude=True)
    """The OpenAI client used to generate responses."""

    def _generate(self) -> str:
        """Generates a response using the message history"""
        messages = [message.to_compatible() for message in self.messages]

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )

        return completion.choices[0].message.content
