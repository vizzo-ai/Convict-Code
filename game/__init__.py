"""Convict Code - core game systems."""

from .state import GameState, GameOverReason
from .zones import Zone, ZoneId, build_prison
from .crew import CrewMember, CrewRole
from .resources import Resources
from .escape import EscapePlan, EscapeComponent
from .actions import Action, ActionResult, AVAILABLE_ACTIONS

__all__ = [
    "GameState",
    "GameOverReason",
    "Zone",
    "ZoneId",
    "build_prison",
    "CrewMember",
    "CrewRole",
    "Resources",
    "EscapePlan",
    "EscapeComponent",
    "Action",
    "ActionResult",
    "AVAILABLE_ACTIONS",
]
