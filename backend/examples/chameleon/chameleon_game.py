from collections import Counter
import random
from typing import ClassVar, List, Type

from hippodrome.game.utils import random_index
from chameleon_player import ChameleonPlayer
from chameleon_data_models import (
    AnimalDescriptionFormat,
    ChameleonGuessFormat,
    HerdVoteFormat,
)

from prompts import fetch_prompt, format_prompt

from hippodrome import Game, Player, Message

from pydantic import Field, field_validator, model_validator

# Default Values
NUMBER_OF_PLAYERS = 6
WINNING_SCORE = 7
AVAILABLE_ANIMALS = [
    "Dog",
    "Cat",
    "Mouse",
    "Hamster",
    "Monkey",
    "Rabbit",
    "Fox",
    "Bear",
    "Panda",
    "Koala",
    "Tiger",
    "Lion",
    "Cow",
    "Pig",
    "Frog",
    "Owl",
    "Duck",
    "Chicken",
    "Butterfly",
    "Turtle",
    "Snake",
    "Octopus",
    "Squid",
    "Hedgehog",
    "Elephant",
    "Rhinoceros",
    "Zebra",
    "Crocodile",
    "Whale",
    "Dolphin",
    "Camel",
    "Giraffe",
    "Deer",
    "Gorilla",
    "Goat",
    "Llama",
    "Horse",
    "Unicorn",
    "Flamingo",
    "Skunk",
    "Shark",
]


class ChameleonGame(Game):
    """The main game class, handles the game logic and player interactions."""

    # Defaults

    winning_score: int = WINNING_SCORE
    """The Number of points required to win the game."""
    available_animals: List[str] = Field(AVAILABLE_ANIMALS, exclude=True)
    """The list of animals that can be chosen as the secret animal."""
    chameleon_ids: List[str] = []
    """Record of which player was the chameleon for each round."""
    herd_animals: List[str] = []
    """Record of what animal was the herd animal for each round."""
    all_animal_descriptions: List[List[dict]] = []
    """Record of the animal descriptions each player has given for each round."""
    chameleon_guesses: List[str] = []
    """Record of what animal the chameleon guessed for each round."""
    herd_vote_tallies: List[List[dict]] = []
    """Record of the votes of each herd member for the chameleon for each round."""

    # Class Variables

    number_of_players: ClassVar[int] = NUMBER_OF_PLAYERS
    """The number of players in the game."""
    player_class: ClassVar[Type[Player]] = ChameleonPlayer
    """The class of the player used in the game."""

    @property
    def chameleon(self) -> ChameleonPlayer:
        """Returns the current chameleon."""
        return self.player_from_id(self.chameleon_ids[-1])

    @property
    def chameleon_id(self) -> str:
        """Returns the current chameleon's id."""
        return self.chameleon_ids[-1]

    @property
    def herd_animal(self) -> str:
        """Returns the current herd animal."""
        return self.herd_animals[-1]

    @property
    def round_animal_descriptions(self) -> List[dict]:
        """Returns the current animal descriptions."""
        return self.all_animal_descriptions[-1]

    @property
    def chameleon_guess(self) -> str:
        """Returns the current chameleon guess."""
        return self.chameleon_guesses[-1]

    @property
    def herd_vote_tally(self) -> List[dict]:
        """Returns the current herd vote tally."""
        return self.herd_vote_tallies[-1]

    async def run_game(self):
        """Starts the game."""

        # Check if the game has not been won
        if self.game_state != "game_end":
            if self.game_state == "game_start":
                await self.game_message(
                    fetch_prompt("game_rules"), message_type="system"
                )
                self.game_state = "setup_round"
            if self.game_state == "setup_round":
                await self.setup_round()
                self.game_state = "animal_description"
            if self.game_state in [
                "animal_description",
                "chameleon_guess",
                "herd_vote",
            ]:
                await self.run_round()
            if self.game_state == "resolve_round":
                await self.resolve_round()

                points = [player.points for player in self.players]

                if max(points) >= self.winning_score:
                    self.game_state = "game_end"
                    self.winner_id = self.players[points.index(max(points))].player_id
                    winner = self.player_from_id(self.winner_id)
                    await self.game_message(f"The game is over {winner.name} has won!")
                    self.end_game()

                else:
                    self.game_state = "setup_round"
                    # Go back to start
                    await self.game_message(
                        f"No player has won yet, the game will end when a player reaches {self.winning_score} points."
                    )
                    await self.game_message(f"Starting a new round...")
                    random.shuffle(self.players)
                    await self.run_game()

    async def run_round(self):
        """Starts the round."""

        # Phase I: Collect Player Animal Descriptions
        if self.game_state == "animal_description":
            for current_player in self.players:
                if current_player.player_id not in [
                    animal_description["player_id"]
                    for animal_description in self.round_animal_descriptions
                ]:

                    response = await self.player_turn_animal_description(current_player)

                    if not response:
                        break

            if len(self.round_animal_descriptions) == len(self.players):
                self.game_state = "chameleon_guess"

        # Phase II: Chameleon Guesses the Animal
        if self.game_state == "chameleon_guess":
            await self.player_turn_chameleon_guess(self.chameleon)

        # Phase III: The Herd Votes for who they think the Chameleon is
        if self.game_state == "herd_vote":
            if not self.awaiting_input:
                self.verbose_message("The Herd is voting...")
            for current_player in self.players:
                if current_player.role == "herd" and current_player.player_id not in [
                    vote["voter_id"] for vote in self.herd_vote_tally
                ]:

                    response = await self.player_turn_herd_vote(current_player)

                    if not response:
                        break

            if len(self.herd_vote_tally) == len(self.players) - 1:
                self.game_state = "resolve_round"

    async def setup_round(self):
        """Sets up the round. This includes assigning roles and gathering player names."""
        # Choose Animal
        herd_animal = self.random_animal()
        self.herd_animals.append(herd_animal)

        # Assign Roles
        chameleon_index = random_index(len(self.players))
        chameleon = self.players[chameleon_index]

        self.chameleon_ids.append(chameleon.player_id)

        await self.game_message(fetch_prompt("assign_chameleon"), chameleon)

        herd = []
        for i, player in enumerate(self.players):
            if i == chameleon_index:
                player.assign_role("chameleon")
            else:
                player.assign_role("herd")
                herd.append(player)

        await self.game_message(
            format_prompt("assign_herd", herd_animal=herd_animal), herd
        )

        for i, player in enumerate(self.players):
            if i == chameleon_index:
                player.assign_role("chameleon")
            else:
                player.assign_role("herd")

        # Empty Animal Descriptions
        self.all_animal_descriptions.append([])

        # Empty Tally for Votes
        self.herd_vote_tallies.append([])

        await self.game_message(
            f"Each player will now take turns describing themselves:"
        )

    async def player_turn_animal_description(self, player: Player):
        """Handles a player's turn to describe themselves."""
        if not self.awaiting_input:
            self.verbose_message(
                f"{player.name} is thinking...", recipient=player, exclude=True
            )
            # await self.game_message(fetch_prompt("player_describe_animal"), player)
            await self.game_message(format_prompt("player_describe_animal"), player)
            # message = Message(sender="game", type="prompt", content=fetch_prompt("player_describe_animal"), recipients=[player.player_id])
            # self.player_response(message)

        # Get Player Animal Description
        response = player.controller.generate_formatted_response(
            AnimalDescriptionFormat
        )

        if response:
            self.round_animal_descriptions.append(
                {"player_id": player.player_id, "description": response.description}
            )
            await self.game_message(
                f"{response.description}", player, exclude=True, sender=player.name
            )
            self.awaiting_input = False
        else:
            self.awaiting_input = True

        return response

    async def player_turn_chameleon_guess(self, chameleon: Player):
        """Handles the Chameleon's turn to guess the secret animal."""
        if not self.awaiting_input:
            await self.game_message(
                "All players have spoken. The Chameleon will now guess the secret animal..."
            )
            self.verbose_message(
                "The Chameleon is guessing...", recipient=chameleon, exclude=True
            )
            player_responses = self.format_animal_descriptions(exclude=self.chameleon)
            await self.game_message(
                format_prompt(
                    "chameleon_guess_animal", player_responses=player_responses
                ),
                self.chameleon,
            )

        response = chameleon.controller.generate_formatted_response(
            ChameleonGuessFormat
        )

        if response:
            self.chameleon_guesses.append(response.animal)
            await self.game_message(
                "The Chameleon has guessed the animal. Now the Herd will vote on who they think the chameleon is."
            )
            self.awaiting_input = False
            self.game_state = "herd_vote"
        else:
            # Await input and do not proceed to the next phase
            self.awaiting_input = True

    async def player_turn_herd_vote(self, player: Player):
        """Handles a player's turn to vote for the Chameleon."""
        if not self.awaiting_input:
            player_responses = self.format_animal_descriptions(exclude=player)
            await self.game_message(
                format_prompt("vote", player_responses=player_responses), player
            )

        # Get Player Vote
        additional_fields = {
            "player_names": [p.name for p in self.players if p != player]
        }
        response = player.controller.generate_formatted_response(
            HerdVoteFormat, additional_fields=additional_fields
        )

        if response:
            await self.debug_message(
                f"{player.name} voted for {response.vote}",
                recipient=player,
                exclude=True,
            )

            voted_for_player = self.player_from_name(response.vote)

            player_vote = {
                "voter_id": player.player_id,
                "voted_for_id": voted_for_player.player_id,
            }

            self.herd_vote_tally.append(player_vote)
            self.awaiting_input = False
        else:
            self.awaiting_input = True

        return response

    async def resolve_round(self):
        """Resolves the round, assigns points, and prints the results."""
        await self.game_message("All players have voted!")
        for vote in self.herd_vote_tally:
            voter = self.player_from_id(vote["voter_id"])
            voted_for = self.player_from_id(vote["voted_for_id"])
            await self.game_message(f"{voter.name} voted for {voted_for.name}")

        accused_player_id = self.count_chameleon_votes(self.herd_vote_tally)

        await self.game_message(f"The round is over. Calculating results...")
        await self.game_message(
            f"The Chameleon was {self.chameleon.name}, and they guessed the secret animal was {self.chameleon_guess}."
        )
        await self.game_message(
            f"The secret animal was actually was {self.herd_animal}."
        )

        if accused_player_id:
            accused_name = self.player_from_id(accused_player_id).name
            await self.game_message(
                f"The Herd voted for {accused_name} as the Chameleon."
            )
        else:
            await self.game_message(f"The Herd could not come to a consensus.")

        # Point Logic
        # If the Chameleon guesses the correct animal    =   +1 Point to the Chameleon
        if self.chameleon_guess.lower() == self.herd_animal.lower():
            self.chameleon.points += 1

        # If the Chameleon guesses the incorrect animal  =   +1 Point to each Herd player
        else:
            for player in self.players:
                if player.role == "herd":
                    player.points += 1
        # If a Herd player votes for the Chameleon       =   +1 Point to that player
        for vote in self.herd_vote_tally:
            if vote["voted_for_id"] == self.chameleon.player_id:
                self.player_from_id(vote["voter_id"]).points += 1

        # If the Herd fails to accuse the Chameleon      =   +1 Point to the Chameleon
        if not accused_player_id or accused_player_id != self.chameleon.player_id:
            self.chameleon.points += 1

        # Print Scores
        player_points = "\n".join(
            [f"{player.name}: {player.points}" for player in self.players]
        )
        await self.game_message(f"Current Game Score:\n{player_points}")

    def random_animal(self) -> str:
        """Returns a random animal from the list of available animals, and removes it from the list."""
        animal = random.choice(self.available_animals)
        self.available_animals.remove(animal)
        return animal

    @staticmethod
    def count_chameleon_votes(player_votes: list[dict]) -> str | None:
        """Counts the votes for each player."""
        votes = [vote["voted_for_id"] for vote in player_votes]

        freq = Counter(votes)
        most_voted_player, number_of_votes = freq.most_common()[0]

        # If one player has more than 50% of the votes, the herd accuses them of being the chameleon
        if number_of_votes / len(player_votes) >= 0.5:
            return most_voted_player
        else:
            return None

    def format_animal_descriptions(self, exclude: Player = None) -> str:
        """Formats the animal description responses of the players into a single string."""
        formatted_responses = ""
        for response in self.round_animal_descriptions:
            # Used to exclude the player who is currently responding, so they don't vote for themselves like a fool
            if response["player_id"] != exclude.player_id:
                player = self.player_from_id(response["player_id"])
                formatted_responses += f" - {player.name}: {response['description']}\n"

        return formatted_responses
