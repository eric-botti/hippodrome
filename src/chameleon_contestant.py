from typing import List, Literal

from gauntlet.contestant import ContestantSubclass

Role = Literal["chameleon", "herd"]


class ChameleonContestant(ContestantSubclass):
    """A player in the game Chameleon"""

    points: int = 0
    """The number of points the player has."""
    roles: List[Role] = []
    """The role of the player in the game. Can be "chameleon" or "herd". This changes every round."""

    def assign_role(self, role: Role):
        self.roles.append(role)

    @property
    def role(self) -> Role:
        """The current role of the player."""
        return self.roles[-1]

    @property
    def rounds_played_as_chameleon(self) -> int:
        """The number of times the player has been the Chameleon."""
        return self.roles.count("chameleon")

    @property
    def rounds_played_as_herd(self) -> int:
        """The number of times the player has been in the Herd."""
        return self.roles.count("herd")
