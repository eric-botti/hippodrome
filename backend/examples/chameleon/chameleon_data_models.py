from typing import List

from hippodrome.output_formats import OutputFormatModel
from pydantic import Field, field_validator, model_validator


class AnimalDescriptionFormat(OutputFormatModel):
    # Define fields of our class here
    description: str = Field(description="A brief description of the animal")
    """A brief description of the animal"""

    @field_validator("description")
    @classmethod
    def check_starting_character(cls, v) -> str:
        if not v[0].upper() == "I":
            raise ValueError(
                "Please rewrite your description so that it begins with 'I'"
            )
        return v


class ChameleonGuessFormat(OutputFormatModel):
    animal: str = Field(
        description="Name of the animal you think the Herd is in its singular form, e.g. 'animal' not 'animals'"
    )

    @field_validator("animal")
    @classmethod
    def is_one_word(cls, v) -> str:
        if len(v.split()) > 1:
            raise ValueError("Animal's name must be one word")
        return v


class HerdVoteFormat(OutputFormatModel):
    player_names: List[str] = Field([], exclude=True)
    """The names of the players in the game"""
    vote: str = Field(description="The name of the player you are voting for")
    """The name of the player you are voting for"""

    @model_validator(mode="after")
    def check_player_exists(self) -> "HerdVoteFormat":
        if self.vote.lower() not in [player.lower() for player in self.player_names]:
            raise ValueError(
                f"Player {self.vote} does not exist, please vote for one of {self.player_names}"
            )
        return self
