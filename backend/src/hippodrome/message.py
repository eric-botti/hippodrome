from typing import Literal, List
from pydantic import BaseModel, computed_field, Field

MessageType = Literal["prompt", "info", "agent", "retry", "error", "format", "verbose", "debug", "system"]

message_number = 0


def next_message_number():
    global message_number
    current_message_number = message_number
    message_number += 1
    return current_message_number


class Message(BaseModel):
    """A generic message, these are used to communicate between the game and the players."""

    sender: str = ""
    """The id of the sender of the message."""
    type: MessageType
    """The type of the message."""
    content: str
    """The content of the message."""
    recipients: List[str] = Field(default_factory=list)
    """The id/ids of the players that the message was sent by/to."""

    @property
    def conversation_role(self) -> str:
        """The message type in the format used by the LLM."""

        # Most LLMs expect the "prompt" to come from a "user" and the "response" to come from an "assistant"
        # Since the contestants are the ones responding to messages, take on the llm_type of "assistant"
        # This can be counterintuitive since they can be controlled by either human or ai
        # Further, The programmatic messages from the game are always "user"

        if self.type != "system":
            return "system"
        elif self.type != "agent":
            return "user"
        else:
            return "assistant"

    @property
    def requires_response(self) -> bool:
        """Returns True if the message requires a response."""
        return self.type in ["prompt", "retry", "format"]

    def to_compatible(self) -> dict[str, str]:
        """Returns the message in a conversation compatible format for most APIs."""
        return {"role": self.conversation_role, "content": self.content}


class AgentMessage(Message):
    """A message that has been sent to 1 or more contestants."""

    game_id: str
    """The id of the game the message was sent during."""
    message_number: int = Field(default_factory=next_message_number)
    """The number of the message, indicating the order in which it was sent."""

    @computed_field
    def message_id(self) -> str:
        """Returns the message id in the format used by the LLM."""
        return f"{self.game_id}-{self.message_number}"

    @classmethod
    def from_message(cls, message: Message, recipients: List[str], game_id: str) -> "AgentMessage":
        """Creates an AgentMessage from a Message."""
        return cls(
            sender=message.sender,
            type=message.type,
            content=message.content,
            recipients=recipients,
            game_id=game_id
        )