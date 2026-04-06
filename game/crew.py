"""Crew members: roles, loyalty, recruitment, and betrayal checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class CrewRole(str, Enum):
    FIXER = "fixer"
    MUSCLE = "muscle"
    BRAINS = "brains"
    INSIDER = "insider"
    WILDCARD = "wildcard"


BETRAYAL_THRESHOLD = 30


@dataclass
class CrewMember:
    id: str
    name: str
    role: CrewRole
    bio: str = ""
    secret: str = ""
    price: str = ""
    loyalty: int = 40
    recruited: bool = False
    known_secrets: List[str] = field(default_factory=list)

    def adjust_loyalty(self, delta: int) -> None:
        self.loyalty = max(0, min(100, self.loyalty + delta))

    def is_at_risk(self) -> bool:
        """Below this threshold, the crew member may inform under pressure."""
        return self.loyalty < BETRAYAL_THRESHOLD

    def will_commit(self) -> bool:
        """Whether they'll actually participate in the escape."""
        return self.recruited and self.loyalty >= 50


def default_crew_pool() -> List[CrewMember]:
    """The recruitable NPCs for the prototype."""
    return [
        CrewMember(
            id="reese",
            name="Reese",
            role=CrewRole.FIXER,
            bio="Smokes too much, smiles too easy. Knows which guards take cash.",
            secret="Owes a gambling debt to a gang on the outside.",
            price="A clean slate on his debt.",
            loyalty=45,
        ),
        CrewMember(
            id="boone",
            name="Boone",
            role=CrewRole.MUSCLE,
            bio="Ex-boxer. Quiet. Eats alone. Doesn't start things, but ends them.",
            secret="His son visits under a fake name.",
            price="A promise that his son never hears about this.",
            loyalty=35,
        ),
        CrewMember(
            id="marguerite",
            name="Marguerite",
            role=CrewRole.BRAINS,
            bio="Former accountant. Does the Times crossword in ink.",
            secret="She's done this before. It didn't work.",
            price="To not be left behind this time.",
            loyalty=50,
        ),
        CrewMember(
            id="doc",
            name='"Doc" Halloran',
            role=CrewRole.INSIDER,
            bio="Prison trustee. Runs meds between the infirmary and the blocks.",
            secret="He's being blackmailed by a guard.",
            price="The guard, dealt with — one way or another.",
            loyalty=40,
        ),
        CrewMember(
            id="cricket",
            name="Cricket",
            role=CrewRole.WILDCARD,
            bio="Nobody knows his real name. Talks to the walls. Also talks to the right people.",
            secret="Not what he seems. At all.",
            price="Unclear. Shifts every week.",
            loyalty=30,
        ),
    ]
