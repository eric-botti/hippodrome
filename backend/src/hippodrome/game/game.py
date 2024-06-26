import asyncio
from typing import Optional, Type, List, ClassVar

from pydantic import BaseModel, Field

from hippodrome.output_formats import OutputFormatModel
from hippodrome.player import Player
from hippodrome.game.utils import *
from hippodrome.controllers import BaseController

from hippodrome.message import Message, MessageType, AgentMessage

from hippodrome.controllers import (
    OpenAIController,
    BaseHumanController,
    HumanCLIController,
)


from hippodrome.data_collection import save


# Abstracting the Game Class is a WIP so that future games can be added
class Game(BaseModel):
    """Base class for all games."""

    # Required
    game_id: str
    """The unique id of the game."""
    players: List[Player] = Field(exclude=True)
    """The players in the game."""
    observer: Optional[Player]
    """An observer who can see all public messages, but doesn't actually play."""

    # Default
    winner_id: str | None = None
    """The id of the player who has won the game."""
    game_state: str = Field("game_start", exclude=True)
    """Keeps track of the current state of the game."""
    awaiting_input: bool = Field(False, exclude=True)
    """Whether the game is currently awaiting input from a player."""
    messages: List[Message] = Field(default_factory=list)
    """The messages sent during the game."""
    message_queue: List[Message] = asyncio.Queue()
    """A queue of messages to be sent during the game, these are relayed to the players as they are added."""

    # Class Variables
    number_of_players: ClassVar[int]
    """The number of players in the game."""
    player_class: ClassVar[Type[Player]] = Player
    """The class of the player used in the game."""

    def player_from_id(self, player_id: str) -> Player:
        """Returns a player from their ID."""
        return next(
            (player for player in self.players if player.player_id == player_id), None
        )

    def player_from_name(self, name: str) -> Player:
        """Returns a player from their name."""
        return next(
            (player for player in self.players if player.name.lower() == name.lower()),
            None,
        )

    async def game_message(
        self,
        content: str,
        recipient: (
            Player | List[Player] | None
        ) = None,  # If None, message is broadcast to all players
        exclude: bool = False,  # If True, the message is broadcast to all players except the chosen player
        message_type: MessageType = "info",
        sender: str = "game",
    ):
        """
        Sends a message to a player or all players.
        If no recipient is specified, the message is broadcast to all players.
        If exclude is True, the message is broadcast to all players except the recipient.
        Some message types are only available to player with access (e.g. verbose, debug).
        """
        if exclude or not recipient:
            # These are public messages, exclude is used to exclude the sender from the recipient list.
            recipients = [player for player in self.players if player != recipient]
            if self.observer:
                recipients.append(self.observer)
        else:
            if isinstance(recipient, Player):
                recipients = [recipient]
            else:
                recipients = recipient

        message = Message(sender=sender, type=message_type, content=content)
        recipient_ids = []

        for player in recipients:
            if player.can_receive_message(message_type):
                player.controller.add_message(message)
                recipient_ids.append(player.player_id)

        agent_message = AgentMessage.from_message(message, recipient_ids, self.game_id)

        self.add_message(agent_message)

    async def verbose_message(self, content: str, **kwargs):
        """
        Sends a verbose message to all players capable of receiving them.
        Verbose messages are used to communicate in real time what is happening that cannot be seen publicly.

        Ex: "Abby is thinking..."
        """
        self.game_message(content, **kwargs, message_type="verbose")

    async def debug_message(self, content: str, **kwargs):
        """
        Sends a debug message to all players capable of receiving them.
        Debug messages usually contain secret information and should only be sent when it wouldn't spoil the game.

        Ex: "Abby is the chameleon."
        """
        await self.game_message(content, **kwargs, message_type="debug")

    # WIP
    async def get_player_response(
        self, message: Message, output_format: Type[OutputFormatModel] = None
    ):
        """
        Sends a game message to a player (or list of players) and waits for a response from each of them.
        The response is then saved and returned.
        """
        # Add the message to the game history
        self.add_message(message)

        # For each recipient, generate a response
        for player_id in message.recipients:
            player = self.player_from_id(player_id)

            # Filter messages to only include messages sent by or to the player
            player_messages = [
                m
                for m in self.messages
                if message.sender == player_id or player_id in message.recipients
            ]

            if player.controller.is_ai:
                # If the player is an AI, format the messages appropriately
                player_messages = [message.to_compatible() for message in self.messages]

            player.controller.messages = player_messages

            # Generate a response
            new_message = player.controller.generate_response()

            # Add the response to the game history
            if new_message is not None:
                self.add_message(new_message)

    def add_message(self, message: Message):
        """Adds a message to the game history."""

        self.messages.append(message)
        save(message)

    async def run_game(self):
        """Runs the game."""
        raise NotImplementedError(
            "The run_game method must be implemented by the subclass."
        )

    def end_game(self):
        """Ends the game and declares a winner."""
        for player in self.players:
            save(player)

        save(self)

    @classmethod
    def from_human_name(
        cls,
        human_name: str = None,
        human_interface: Type[BaseHumanController] = HumanCLIController,
        human_message_level: str = "verbose",
    ):
        """
        Instantiates a game with a human player if a name is provided.
        Otherwise, the game is instantiated with all AI players and an observer.
        """
        game_id = generate_game_id()

        # Gather Player Names
        if human_name:
            ai_names = random_names(cls.number_of_players - 1, human_name)
            human_index = random_index(cls.number_of_players)
        else:
            ai_names = random_names(cls.number_of_players)
            human_index = None

        # Add Players
        players = []

        for i in range(0, cls.number_of_players):
            player_dict = {"game_id": game_id}

            if human_index == i:
                player_dict["name"] = human_name
                player_id = f"{game_id}-human"
                player_dict["controller"] = human_interface(
                    agent_id=player_id, game_id=game_id
                )
                player_dict["message_level"] = human_message_level
            else:
                player_dict["name"] = ai_names.pop()
                player_id = f"{game_id}-{player_dict['name']}"
                # all AI players use the OpenAI interface for now - this can be changed in the future
                player_dict["controller"] = OpenAIController(
                    agent_id=player_id, game_id=game_id
                )
                player_dict["message_level"] = "info"

            player_dict["player_id"] = player_id
            players.append(cls.player_class(**player_dict))

        # Add Observer - an Agent who can see all the messages, but doesn't actually play
        if human_index is None:
            observer = Player.observer(game_id, controller_type=human_interface)
        else:
            observer = None

        return cls(game_id=game_id, players=players, observer=observer)

    @classmethod
    def from_controllers(cls, controllers: List[BaseController]):
        """
        Instantiates a game with a list of controllers.
        """
        game_id = generate_game_id()

        players = []

        if len(controllers) != cls.number_of_players:
            raise ValueError(
                f"Expected {cls.number_of_players} controllers, but got {len(controllers)}."
            )

        player_names = random_names(cls.number_of_players)

        for i, controller in enumerate(controllers):
            player = cls.player_class(
                game_id=game_id,
                controller=controller,
                name=player_names[i],
                player_id=f"{game_id}-{controller.agent_id}",
            )

            players.append(player)

        return cls(game_id=game_id, players=players, observer=None)
