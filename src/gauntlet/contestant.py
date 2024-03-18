from typing import Literal, List, Type

from pydantic import BaseModel, Field

from gauntlet.controllers import BaseController, HumanCLIController

from message import MessageType


# Abstraction is a WIP and a little premature, but I'd like to reuse this framework to create more Games in the future
class Contestant(BaseModel):
    """Base class for a player"""

    name: str
    """The name of the player."""
    player_id: str
    """The id of the player."""
    game_id: str
    """The id of the game the player is in."""
    controller: BaseController = Field(exclude=True)
    """The interface used by the agent controlling the player to communicate with the game."""
    message_level: str = "info"
    """The level of messages that the player will receive. Can be "info", "verbose", or "debug"."""

    def can_receive_message(self, message_type: MessageType) -> bool:
        """Returns True if the player can receive a message of the type."""
        if message_type == "verbose" and self.message_level not in ["verbose", "debug"]:
            return False
        elif message_type == "debug" and self.message_level != "debug":
            return False
        else:
            return True

    @classmethod
    def observer(
            cls,
            game_id: str,
            message_level: str = "verbose",
            controller_type: Type[BaseController] = HumanCLIController
    ):
        """Creates an observer player."""
        name = "Observer"
        player_id = f"{game_id}-observer"
        controller = controller_type(agent_id=player_id, game_id=game_id)

        return cls(name=name, player_id=player_id, game_id=game_id, controller=controller, message_level=message_level)


class ContestantSubclass(Contestant):
    @classmethod
    def from_player(cls, player: Contestant):
        """Creates a new instance of the subclass from a player instance."""
        fields = player.model_dump()
        fields['controller'] = player.controller
        return cls(**fields)
